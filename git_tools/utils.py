
class PrintableObject(object):
    def __str__(self):
        ret = "%s(" % self.__class__.__name__
        keys = list(self.__dict__.keys())

        for i in range(len(keys)):
            ret += "%s=%s" % (keys[i], self.__dict__[keys[i]])
            if i < (len(keys) - 1):
                ret += ", "

        return ret

    def __repr__(self):
        return self.__str__()

