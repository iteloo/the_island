import collections


class ObservedData:

    def __init__(self):
        self._observers = set()
        self._callbacks = {}

    def add_observer(self, observer, callback):
        self._observers.add(observer)
        self._callbacks[observer] = callback

    def remove_observer(self, observer):
        self._observers.remove(observer)
        del self._callbacks[observer]


class ItemCreatedNotification():

    def __init__(self, key, value):
        self.key = key
        self.value = key


class ItemChangedNotification():

    def __init__(self, key, value, old_value):
        self.key = key
        self.value = value
        self.old_value = old_value


class ItemDeletedNotification:

    def __init__(self, key, value):
        self.key = key
        self.value = value


class ObservedList(collections.MutableSequence, ObservedData):
    """A list that notify an observer of change"""

    def __init__(self, *args, **kwargs):
        super().__init__()
        self._list = list(*args, **kwargs)

    def __str__(self):
        return self._list.__str__()

    def __getitem__(self, key):
        return self._list[key]

    def __setitem__(self, key, value):
        try:
            old_value = self._list[key]
            self._list[key] = value
        except:
            pass
        else:
            if not value is old_value:
                for o in self._observers:
                    self._callbacks[o](self, ItemChangedNotification(key, value, old_value))

    def __delitem__(self, key):
        try:
            deleted_item = self._list[key]
            del self._list[key]
        except:
            raise
        else:
            for o in self._observers:
                self._callbacks[o](self, ItemDeletedNotification(key, deleted_item))

    def __iter__(self):
        return iter(self._list)

    def __len__(self):
        return len(self._list)

    def insert(self, index, value):
        try:
            self._list.insert(index, value)
        except:
            pass
        else:
            for o in self._observers:
                self._callbacks[o](self, ItemCreatedNotification(index, value))

    def copy(self):
        return self._list.copy()


class ObservedDict(collections.MutableMapping, ObservedData):
    """A dictionary that notify an observer of change"""

    def __init__(self, *args, **kwargs):
        super().__init__()
        self._dict = dict(*args, **kwargs)

    def __str__(self):
        return self._dict.__str__()

    def __getitem__(self, key):
        return self._dict[key]

    def __setitem__(self, key, value):
        key_exists = key in self._dict
        if key_exists:
            old_value = self._dict[key]
        self._dict[key] = value
        # if key existed and value changed, notify observer of change
        if key_exists:
            if not value is old_value:
                for o in self._observers:
                    self._callbacks[o](self, ItemChangedNotification(key, value, old_value))
        # if key didn't exist, notify observer of creation
        else:
            for o in self._observers:
                self._callbacks[o](self, ItemCreatedNotification(key, value))

    def __delitem__(self, key):
        try:
            deleted_item = self._dict[key]
            del self._dict[key]
        except:
            raise
        else:
            for o in self._observers:
                self._callbacks[o](self, ItemDeletedNotification(key, deleted_item))

    def __iter__(self):
        return iter(self._dict)

    def __len__(self):
        return len(self._dict)

    def copy(self):
        return self._dict.copy()

if __name__ == '__main__':
    ob = object()
    a = ObservedDict({1:2, 4:5})
    a.add_observer(ob)
    a[1] = 3