from backend import helpers

import tornado.websocket
import functools
import json
import collections
import inspect


# noinspection PyAttributeOutsideInit
class MessageHandler(tornado.websocket.WebSocketHandler):
    """Wrap WebSocket communication following the 'method-call' message format described in https://github.com/iteloo/the_island/wiki/Server-client-interface.

    Each instance of `MessageHandler` is tied to a delegate object. To use `MessageHandler`, you must:
        1. pass a `delegateClass` to initialize(),
        2. import `message.py` in the file where you define your `delegateClass`
        3. add `message.MessageDelegate` as a parent class `delegateClass`; and
        4. using the `message.MessageDelegate.sending` decorator, wrap each member method for which you want a method-call message to be generated

    You may also optionally implement `on_open()` and `on_close()` that will be called when the socket is opened and closed, respectively.


    Detailed description:

    On successful initialization of a websocket connection, an instance of `delegateClass` will be created and set as the delegate of the message handler.

    Message sending:
        When a decorated method on the delegate is called, the message handler will send a matching method-call message through the websocket connection. Any argument supplied to the method call will be included in the message as well. In particular, when a callback object is supplied, the handler will store the callback object on the server, and generate a `callback_id` to include in the message.

    Message receiving:
        When a method-call message is received, the handler attempts to invoke a method with matching name on the delegate using any arguments supplied in the message. An exception is raised if no matching methods are found, or if the arguments supplied are inappropriate.
        If a `callback_id` is supplied as part of the arguments, the handler creates a callable wrapper object and pass it to the method as the `callback` argument. When the wrapper object is called, a (new) method-call message to invoke `handle_callback` is sent over the socket connection. The original `callback_id`, along with any arguments passed in when calling the wrapper object, is included in the message.

    """

    def __str__(self):
        return "Message handler for %s" % self.delegate

    # this replaces __init__ (in fact it seems to be called before __init__)
    def initialize(self, delegate_class=None):
        # make new delegate object
        assert delegate_class
        assert issubclass(delegate_class, MessageDelegate)
        self.delegate = delegate_class(self)

        # callback-sending handling vars
        self._current_callback_id = 0
        self._callback_with_id = {}

    ### socket connection handling ###

    def open(self):
        # notify delegate
        call_on(self.delegate, 'on_open', check_error=False)

    def on_message(self, message):

        # logging
        helpers.cprint("==> Received message from client: ", helpers.LColor.INCOMING)
        print(message)

        # All messages will follow the format described in https://github.com/iteloo/the_island/wiki/Server-client-interface
        try:
            try:
                msg = json.loads(message)
            except ValueError:
                raise InvalidMessageFormatError

            # A proper message consists of a method and a dictionary of kwargs
            method_name = msg.get('method')
            kwargs = msg.get('args', {}).copy()
            if method_name:
                # handle `handle_callback` method calls
                if method_name == 'handle_callback':
                    # a `handle_callback` call must come with a `callback_id` and optionally `callback_args` as `args`
                    # it must not include anything else
                    callback_id = kwargs.pop('callback_id', None)
                    callback_args = kwargs.pop('callback_args', {})
                    if callback_id is not None and not kwargs:  # note callback_id can be 0
                        self._handle_callback(callback_id, callback_args)
                    else:
                        raise InvalidArgumentError
                # handle all other method calls
                else:
                    self._invoke(method_name, kwargs)
            else:
                raise InvalidMessageFormatError(msg)
        except (InvalidMessageFormatError, InvalidMethodError, InvalidArgumentError) as err:
            # log error for now
            # todo: more sophisticated error handling
            err_msg = "==> Caught error %s" % type(err).__name__
            if err.args:
                err_msg += " with details:"
            helpers.print_header(err_msg)
            if err.args:
                print(err.args)
        else:
            # send a receipt if no error
            # self._send_receipt(message)
            pass

    def on_close(self):
        # notify delegate
        call_on(self.delegate, 'on_close', check_error=False)
        # remove delegate
        self.delegate = None

    def write_message(self, message, binary=False):
        # logging
        helpers.cprint("==> Sending message to client: ", helpers.LColor.OUTGOING)
        print(message)
        # call original
        super().write_message(message, binary)

    ### method-call handling ###

    def _invoke(self, method_name, kwargs):
        """Attempt to call the method on delegate with the specified arguments

        If a `callback_id` is present, `_invoke` will create a wrapper object that, when called, will send a `handle_callback` message over the socket. The wrapper object is passed into the method along with the rest of the arguments.

        """

        # if a `callback_id` is included, replace it with a python `callback` object that wraps the `handle_callback` method-call on the client
        if 'callback_id' in kwargs:
            # create a callback object that wraps the `handle_callback` method call on the client and replace `callback_id` by the `callback` object
            kwargs['callback'] = self._generate_callback(kwargs['callback_id'])
            kwargs.pop('callback_id')

        # attempt to invoke method on delegate
        call_on(self.delegate, method_name, **kwargs)

    def _handle_callback(self, callback_id, callback_args):
        """Handle a callback

        Attempt to:
            1. find a callback object matching the `callback_id`
            2. call the callback object with `callback_args`

        """

        # attempt to retrieve callback object using `callback_id`
        callback = self._retrieve_callback(callback_id)
        # attempt to invoke callback using `callback_args`
        call(callback, **callback_args)

    def _send_receipt(self, message_received):
        msg = {'method': 'handle_receipt', 'args': {'message_received': message_received}}
        self.write_message(json.dumps(msg))

    ### helpers (attaching a callbacks in outgoing method calls) ###

    def _register_callback(self, callback):
        """Register a new callback object and return the `callback_id`"""

        # generate callback id
        new_callback_id = self._generate_callback_id()
        self._callback_with_id[new_callback_id] = callback
        return new_callback_id

    def _retrieve_callback(self, callback_id):
        """Return registered callback object with matching `callback_id`

        An exception is raised if the callback cannot be found.

        """

        try:
            return self._callback_with_id.pop(callback_id)
        except KeyError:
            # todo: is there a more fitting type of error?
            raise InvalidArgumentError(callback_id)

    def _generate_callback_id(self):
        """Generate a unique `callback_id`"""

        _currentCallbackId = self._current_callback_id
        self._current_callback_id += 1
        return _currentCallbackId

    ### helpers (handling callback attached with incoming method calls)

    def _generate_callback(self, callback_id):
        """Create a wrapper object that, when called, will send a `handle_callback` message over the socket.

        The kwargs passed to the wrapper object, along with the `callback_id` when creating the object, will be passed as arguments to the `handle_callback` message.

        """

        def callback(**callback_args):
            # create message
            msg = {
                'method': 'handle_callback',
                'args': {
                    'callback_id': callback_id,
                }
            }
            if callback_args:
                msg['args']['callback_args'] = callback_args

            # send message to client
            # problem: what if delegate disconnects before callback?
            self.write_message(json.dumps(msg))

        return callback

    ### delegate properties

    @property
    def delegate(self):
        return self._delegate

    @delegate.setter
    def delegate(self, value):
        self._delegate = value


### Message delegate ###

# noinspection PyProtectedMember
class MessageDelegate(object):

    def __init__(self, message_handler):
        # add handler ivar
        self._message_handler = message_handler


def sending(method):
    """A decorator that calls the method on the client by sending a message over websocket"""

    # noinspection PyProtectedMember
    @functools.wraps(method)
    def wrapper(self, *args, **kwargs):
        # self should be the `delegate` object here

        # call local (server-side) method first
        method(self, *args, **kwargs)

        # prepare dictionary of args
        callargs = inspect.getcallargs(method, self, *args, **kwargs)
        callargs.pop('self')

        # if our method takes in a callback
        if 'callback' in callargs:
            # store callback object on server-side (and remove from message)
            callback_id = self._message_handler._register_callback(callargs.pop('callback'))
            # attach callback id to message
            callargs['callback_id'] = callback_id

        # create message
        msg = {'method': method.__name__, 'args': callargs}

        # send message to client
        msg = json.dumps(msg)
        self._message_handler.write_message(msg)

    return wrapper


def forward(recipient):
    """Return a decorator that attempts to call a method with the same name on the recipient

    The recipient can either be an object or the path to the object in string, in which case the object will be searched for each time the decorated method is called.

    """

    # the decorator
    def decorator(method):
        @functools.wraps(method)
        def wrapper(*args, **kwargs):
            # if recipient is a path, attempt to get actual object
            if isinstance(recipient, str):
                path = recipient.split('.')
                # retrieve recipient object
                try:
                    # object will be looked for in the scope of `method`
                    r = inspect.getcallargs(method, *args, **kwargs)[path.pop(0)]
                    for attr in path:
                        r = getattr(r, attr)
                except (NameError, AttributeError):
                    # re-raise for now
                    raise
            else:
                r = recipient
            # call method on recipient
            call_on(r, method.__name__, *args, **kwargs)

        return wrapper

    return decorator


### errors ###

class InvalidMethodError(Exception):
    pass


class InvalidArgumentError(Exception):
    pass


class InvalidMessageFormatError(Exception):
    pass


### method calling helpers ###

def call(method, *args, check_error=True, **kwargs):
    """Attempt to call the method

    If a matching method cannot be found, an InvalidMethodError is raised. If the arguments are invalid, an InvalidArgumentError is raised. Setting the `check_error` option to False will suppress these errors.

    """

    try:
        if method and isinstance(method, collections.Callable):
            # todo: This will mask any TypeError exceptions we might not want to mask
            try:
                return method(*args, **kwargs)
            except TypeError:
                raise InvalidArgumentError(args, kwargs)
        else:
            raise InvalidMethodError
    except (InvalidMethodError, InvalidArgumentError):
        if check_error:
            raise


def call_on(recipient, method_name, *args, check_error=True, **kwargs):
    """Attempt to call a method with the same name on the recipient

    If a matching method cannot be found, an InvalidMethodError is raised. If the arguments are invalid, an InvalidArgumentError is raised. Setting the `check_error` option to False will suppress these errors.

    """

    method = getattr(recipient, method_name, None)
    call(method, *args, check_error=check_error, **kwargs)
