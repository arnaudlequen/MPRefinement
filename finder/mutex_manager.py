import attr


@attr.s
class MutexManager:
    mutexes: set = attr.ib(default=attr.Factory(set))

    def __contains__(self, mutex):
        if not isinstance(mutex, set) or len(mutex) != 2:
            return False

        if self._hash_mutex(mutex) in self.mutexes:
            return True

        return False

    def add(self, mutex):
        self.mutexes.add(self._hash_mutex(mutex))

    def __iter__(self):
        for hashed_mutex in self.mutexes:
            yield self._unhash_mutex(hashed_mutex)

    @staticmethod
    def _hash_mutex(mutex):
        f1_id, f2_id = min(mutex), max(mutex)
        return f'{f1_id}_{f2_id}'

    @staticmethod
    def _unhash_mutex(hashed_mutex):
        return set(map(int, hashed_mutex.split('_')))

