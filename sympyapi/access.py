class Access:
    codes = dict(
        GUEST = 0,
        ADMIN = 1,
        LOGIN = 2,
        PAYED = 4)

    def __call__(self, *args):
        self.calc(*args)

    @classmethod
    def calc(cls, *codes):
        res_code = 0
        for c in codes:
            res_code += cls.codes[c]
        return res_code

    @classmethod
    def check(cls, required_code, user_code):
        return required_code == (required_code & user_code)

