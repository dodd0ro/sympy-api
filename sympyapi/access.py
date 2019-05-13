class Access:
    codes = dict(
        GUEST = 0,
        ADMIN = 1,
        LOGIN = 2,
        PAYED = 4)

    def __call__(self, *args):
        self.calc(*args)

    @classmethod
    def calc(cls, *args):
        code = 0
        for code in args:
            code += cls.codes[code]
        return code

    @classmethod
    def check(cls, target_code, user_code):
        return target_code == (target_code & user_code)

