# Copyright (C) 2017 Xomad. All rights reserved.
#
# Created on 2/13/17


class Demographic(dict):
    CATEGORY_AGE = 'age'
    CATEGORY_BRAND = 'brand'
    CATEGORY_CITY = 'city'
    CATEGORY_ETHNICITY = 'ethnicity'
    CATEGORY_FAMILY_STATUS = 'family_status'
    CATEGORY_GENDER = 'gender'
    CATEGORY_INTEREST = 'interest'
    CATEGORY_PERSONAL_INCOME = 'personal_income'
    CATEGORY_TAG = 'tag'
    ALL_CATEGORIES = [CATEGORY_AGE, CATEGORY_BRAND, CATEGORY_CITY, CATEGORY_ETHNICITY, CATEGORY_FAMILY_STATUS,
                      CATEGORY_GENDER, CATEGORY_INTEREST, CATEGORY_PERSONAL_INCOME, CATEGORY_TAG]

    def __init__(self, *args, **kwargs):
        super(Demographic, self).__init__(*args, **kwargs)

    def __bool__(self):
        return any((
            self.get(Demographic.CATEGORY_AGE), self.get(Demographic.CATEGORY_BRAND),
            self.get(Demographic.CATEGORY_CITY), self.get(Demographic.CATEGORY_ETHNICITY),
            self.get(Demographic.CATEGORY_FAMILY_STATUS), self.get(Demographic.CATEGORY_GENDER),
            self.get(Demographic.CATEGORY_INTEREST), self.get(Demographic.CATEGORY_PERSONAL_INCOME),
            self.get(Demographic.CATEGORY_TAG)
        ))

    def __set_item__(self, key, value):
        if key in self.ALL_CATEGORIES and isinstance(value, dict):
            return
        self[key] = value

    @staticmethod
    def from_dict(a_dict):
        return Demographic({_: a_dict[_] for _ in Demographic.ALL_CATEGORIES if _ in a_dict and a_dict[_]})

    def put(self, category, key, value):
        if category not in self.ALL_CATEGORIES:
            raise AttributeError('category %s is invalid' % category)
        if category in self:
            self[category][key] = value
        else:
            self[category] = {key: value}

    def put_age(self, key, value):
        self.put(Demographic.CATEGORY_AGE, key, value)

    def put_brand(self, key, value):
        self.put(Demographic.CATEGORY_BRAND, key, value)

    def put_city(self, key, value):
        self.put(Demographic.CATEGORY_CITY, key, value)

    def put_ethnicity(self, key, value):
        self.put(Demographic.CATEGORY_ETHNICITY, key, value)

    def put_family_status(self, key, value):
        self.put(Demographic.CATEGORY_FAMILY_STATUS, key, value)

    def put_gender(self, key, value):
        self.put(Demographic.CATEGORY_GENDER, key, value)

    def put_interest(self, key, value):
        self.put(Demographic.CATEGORY_INTEREST, key, value)

    def put_personal_income(self, key, value):
        self.put(Demographic.CATEGORY_PERSONAL_INCOME, key, value)

    def put_tag(self, key, value):
        self.put(Demographic.CATEGORY_TAG, key, value)

    def update(self, category, category_payload):
        if category not in self.ALL_CATEGORIES:
            raise AttributeError('category %s is invalid' % category)
        if category in self:
            self[category].update(category_payload)
        else:
            self[category] = category_payload

    def update_age(self, age_payload):
        self.update(Demographic.CATEGORY_AGE, age_payload)

    def update_brand(self, brand_payload):
        self.update(Demographic.CATEGORY_BRAND, brand_payload)

    def update_city(self, city_payload):
        self.update(Demographic.CATEGORY_CITY, city_payload)

    def update_ethnicity(self, ethnicity_payload):
        self.update(Demographic.CATEGORY_ETHNICITY, ethnicity_payload)

    def update_family_status(self, family_status_payload):
        self.update(Demographic.CATEGORY_FAMILY_STATUS, family_status_payload)

    def update_gender(self, gender_payload):
        self.update(Demographic.CATEGORY_GENDER, gender_payload)

    def update_interest(self, interest_payload):
        self.update(Demographic.CATEGORY_INTEREST, interest_payload)

    def update_personal_income(self, personal_income):
        self.update(Demographic.CATEGORY_PERSONAL_INCOME, personal_income)

    def update_tag(self, tag_payload):
        self.update(Demographic.CATEGORY_TAG, tag_payload)


class DemographicPercentage(Demographic):
    @staticmethod
    def _convert_to_percentage(a_dict):
        ret = {}
        if a_dict:
            sum_ = sum(a_dict.values())
            if sum_ > 0:
                for key, value in a_dict.items():
                    ret[key] = float(value) / sum_
        return ret

    @staticmethod
    def from_demographic(demographic):
        if not isinstance(demographic, Demographic):
            raise ValueError('demographic is an instance of % instead of %s' % (type(demographic), Demographic.__name__))

        demographic_percentage = DemographicPercentage()
        for category, category_percentage_payload in demographic.items():
            category_percentage_payload = DemographicPercentage._convert_to_percentage(category_percentage_payload)
            demographic_percentage.update(category, category_percentage_payload)
        return demographic_percentage if demographic_percentage else None
