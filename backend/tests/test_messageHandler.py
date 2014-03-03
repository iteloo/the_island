from unittest import TestCase
from unittest.mock import Mock, patch, call
from tornado.testing import AsyncHTTPTestCase
from tornado.websocket import websocket_connect
from tornado.web import Application
import json

from backend.message import MessageHandler, MessageDelegate, InvalidArgumentError, sending
from backend import helpers


class TestMessageHandlerAPI(AsyncHTTPTestCase):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.mock_delegate = None
        self._websocket_client = None

    def get_app(self):
        _self = self

        class MockDelegate(MessageDelegate):
            def __new__(cls, *args, **kwargs):
                return _self.mock_delegate

        return Application([
            ('/mock', MessageHandler, {'delegate_class': MockDelegate})
        ])

    def test_incoming_method_call_message_without_args(self):
        """Test sending method-call message without args to the server and verifying that the method is correctly called on the delegate"""

        with patch.object(self, 'mock_delegate') as mock_delegate:
            # mock_delegate should stop ioloop when `test_method` is called
            mock_delegate.test_method.side_effect = self.stop
            # send message and pause ioloop
            self.send({'method': 'test_method'})
            self.wait()
            # assert `test_method` is called
            mock_delegate.test_method.assert_called_once_with()

    def test_incoming_method_call_message_with_args(self):
        """Test sending method-call message with args to the server and verifying that the method is correctly called on the delegate"""

        with patch.object(self, 'mock_delegate') as mock_delegate:
            # mock_delegate should stop ioloop when `test_method` is called
            mock_delegate.test_method.side_effect = self.stop
            # send message and pause ioloop
            self.send({'method': 'test_method', 'args': {'param1': 'arg1'}})
            self.wait()
            # assert `test_method` is called
            mock_delegate.test_method.assert_called_once_with(param1='arg1')

    def test_incoming_method_call_with_callback(self):
        """Test handling of callback mechanism"""

        with patch.object(self, 'mock_delegate') as mock_delegate:
            # set callback handling
            def echo(callback, **kwargs):
                callback(**kwargs)
            mock_delegate.echo.side_effect = echo

            # send message
            test_callback_id = 0
            self.send({
                'method': 'echo',
                'args': {
                    'callback_id': test_callback_id,
                    'param1': 'arg1',
                    'param2': 'arg2'
                }
            })

            # wait for `handle_callback` response message
            response_method, response_args = None, None
            while response_method != 'handle_callback':
                response = self.load()
                # todo: add parsing helper
                response_method, response_args = helpers.extract(response, 'method', 'args')

            # check response
            expected_response_args = {
                'callback_id': test_callback_id,
                'callback_args': {
                    'param1': 'arg1',
                    'param2': 'arg2'
                }
            }
            self.assertEqual(response_args, expected_response_args)

    # def test_outgoing_method_call_message(self):
    #     """Test sending outgoing message"""
    #
    #     with patch.object(self, 'mock_delegate', spec=MessageDelegate) as mock_delegate:
    #         # add message-sending method on `mock_delegate`
    #         @sending
    #         def broadcast(self, **kwargs):
    #             pass
    #         mock_delegate.broadcast = Mock()
    #         mock_delegate.broadcast.side_effect = broadcast
    #
    #         # call method
    #         mock_delegate.broadcast(mock_delegate)
    #
    #         # wait for `broadcast` call message on client
    #         response_method, response_args = None, None
    #         while response_method != 'broadcast':
    #             response = self.load()
    #             # todo: add parsing helper
    #             response_method, response_args = helpers.extract(response, 'method', 'args')
    #
    #         print(response_args)
    #
    #         # check response
    #         expected_response_args = {
    #             'callback_id': test_callback_id,
    #             'callback_args': {
    #                 'param1': 'arg1',
    #                 'param2': 'arg2'
    #             }
    #         }
    #         self.assertEqual(response_args, expected_response_args)

    @property
    def websocket_client(self):
        # generate a ws if needed
        if self._websocket_client is None:
            # open a websocket connection
            ws_url = self.get_url('/mock').replace('http', 'ws')
            websocket_connect(ws_url, self.io_loop, callback=self.stop)  # pass a `Future` object into `callback`
            self._websocket_client = self.wait().result()  # get ws from the `Future` object
        return self._websocket_client

    ### convenience ###

    def send(self, msg):
        self.websocket_client.write_message(json.dumps(msg))

    def load(self):
        self.websocket_client.read_message(callback=self.stop)
        return json.loads(self.wait().result())


# noinspection PyProtectedMember
class TestMessageHandler(TestCase):

    def test_initialize_invalid_delegate_class(self):
        """Passing in a `delegate_class` that is not a subclass of `MessageDelegate` should result in an error"""

        invalid_delegate_class = object
        mock_handler = Mock(spec=MessageHandler)
        with self.assertRaises(AssertionError):
            MessageHandler.initialize(mock_handler, invalid_delegate_class)

    def test_initialize_missing_delegate_class(self):
        """Failing to pass in a `delegate_class` should result in an error"""

        mock_handler = Mock(spec=MessageHandler)
        with self.assertRaises(AssertionError):
            MessageHandler.initialize(mock_handler)

    def test_on_message_no_args(self):
        # create test message
        test_method_name = 'method1'
        test_msg = json.dumps({'method': test_method_name})
        # call on mock handler
        mock_handler = Mock(spec=MessageHandler)
        MessageHandler.on_message(mock_handler, test_msg)
        mock_handler._invoke.assert_called_once_with(test_method_name, {})

    def test_on_message_with_args(self):
        # create test message
        test_method_name = 'method1'
        test_args = {'param1': 'arg1', 'param2': 'arg2'}
        test_msg = json.dumps({'method': test_method_name, 'args': test_args})
        # call on mock handler
        mock_handler = Mock(spec=MessageHandler)
        MessageHandler.on_message(mock_handler, test_msg)
        mock_handler._invoke.assert_called_once_with(test_method_name, test_args)

    def test_on_message_handle_callback(self):
        # create test message
        test_callback_id = 0
        test_callback_args = {'cparam1': 'carg1', 'cparam2': 'carg2'}
        test_msg = json.dumps({
            'method': 'handle_callback',
            'args': {
                'callback_args': test_callback_args,
                'callback_id': test_callback_id
            }
        })
        # call on mock handler
        mock_handler = Mock(spec=MessageHandler)
        MessageHandler.on_message(mock_handler, test_msg)
        mock_handler._handle_callback.assert_called_once_with(test_callback_id, test_callback_args)

    def test_on_message_handle_callback_no_callback_args(self):
        # create test message
        test_callback_id = 0
        test_msg = json.dumps({
            'method': 'handle_callback',
            'args': {
                'callback_id': test_callback_id
            }
        })
        # call on mock handler
        mock_handler = Mock(spec=MessageHandler)
        MessageHandler.on_message(mock_handler, test_msg)
        mock_handler._handle_callback.assert_called_once_with(test_callback_id, {})

    def test_on_message_handle_callback_missing_callback_id(self):
        # create test message
        test_msg = json.dumps({
            'method': 'handle_callback',
            'args': {
                'callback_args': {'cparam1': 'carg1', 'cparam2': 'carg2'}
            }
        })
        # call on mock handler
        mock_handler = Mock(spec=MessageHandler)
        with self.assertRaises(InvalidArgumentError):
            MessageHandler.on_message(mock_handler, test_msg)

    def test_on_message_handle_callback_missing_args(self):
        # create test message
        test_msg = json.dumps({
            'method': 'handle_callback'
        })
        # call on mock handler
        mock_handler = Mock(spec=MessageHandler)
        with self.assertRaises(InvalidArgumentError):
            MessageHandler.on_message(mock_handler, test_msg)

    def test_on_message_handle_callback_invalid_arg(self):
        # create test message
        test_msg = json.dumps({
            'method': 'handle_callback',
            'args': {
                'callback_id': 0,
                'callback_args': {'cparam1': 'carg1', 'cparam2': 'carg2'},
                'extra_arg': 'troll'
            }
        })
        # call on mock handler
        mock_handler = Mock(spec=MessageHandler)
        with self.assertRaises(InvalidArgumentError):
            MessageHandler.on_message(mock_handler, test_msg)