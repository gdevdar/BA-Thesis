def drop_bad_observations(df):
    cols_to_fill = ['urban_id','district_id','urban_name','district_name']
    df[cols_to_fill] = df[cols_to_fill].fillna(0)
    df = df[~(df[cols_to_fill] == 0).all(axis=1)].reset_index(drop=True)
    return df

def urban_name_drop_check(item):
    check = item in [
        "კაკლები",
        "კიკეთი",
        "კოჯორი",
        "ოქროყანა",
        "ტაბახმელა",
        "შინდისი",
        "წავკისი",
        "წყნეთი",
        "მუხათგვერდი",
        "მუხათწყარო",
        "ზემო ლისი",
        "თხინვალი",
    ]
    return check

def urban_name_check(item):
    check = item in [
        "ავჭალა",
        "გლდანი",
        "გლდანულა",
        "ზაჰესი",
        "თბილისის ზღვა",
        "თემქა",
        "კონიაკის დას.",
        "ლოტკინი",
        "მუხიანი",
        "ნაძალადევი",
        "სან. ზონა",
        "სოფ. გლდანი",
        "დიდუბე",
        "დიღმის მასივი",
        "კუკია",
        "სვანეთის უბანი",
        "ჩუღურეთი",
        "ბაგები",
        "დიდი დიღომი",
        "დიღომი 1-9",
        "ვაკე",
        "საბურთალო",
        "ვაშლიჯვარი",
        "ვეძისი",
        "კუს ტბა",
        "ლისი",
        "ნუცუბიძის ფერდობი",
        "ვერა",
        "სოფ. დიღომი",
        "აეროპორტის დას.",
        "ვაზისუბანი",
        "ვარკეთილი",
        "ისანი",
        "ლილო",
        "მესამე მასივი",
        "ნავთლუღი",
        "ორთაჭალა",
        "ორხევი",
        "სამგორი",
        "ფონიჭალა",
        "აბანოთუბანი",
        "ავლაბარი",
        "ელია",
        "კრწანისი",
        "მთაწმინდა",
        "სოლოლაკი",
        "მოსკოვის გამზირი",
        "ლისის მიმდებარედ",
        "ივერთუბანი",
        "დიღმის ჭალა",
        "აფრიკა",
        "გიორგიწმინდას დას.",
    ]
    return check

def urban_name_map(item):
    map_dict = {
        "ავჭალა":"Gldani",
        "გლდანი":"Gldani",
        "გლდანულა":"Gldani",
        "ზაჰესი":"Gldani",
        "თბილისის ზღვა":"Nadzaladevi",
        "თემქა":"Nadzaladevi",
        "კონიაკის დას.":"Gldani",
        "ლოტკინი":"Nadzaladevi",
        "მუხიანი":"Gldani",
        "ნაძალადევი":"Nadzaladevi",
        "სან. ზონა":"Nadzaladevi",
        "სოფ. გლდანი":"Gldani",
        "დიდუბე":"Didube",
        "დიღმის მასივი":"Didube",
        "კუკია":"Chughureti",
        "სვანეთის უბანი":"Chughureti",
        "ჩუღურეთი":"Chughureti",
        "ბაგები":"Vake",
        "დიდი დიღომი":"Didi Dighomi",
        "დიღომი 1-9":"Didi Dighomi",
        "ვაკე":"Vake",
        "საბურთალო":"Saburtalo",
        "ვაშლიჯვარი":"Vashlijvari",
        "ვეძისი":"Saburtalo",
        #"თხინვალი":"Saburtalo",
        "კუს ტბა":"Vake",
        "ლისი":"Saburtalo",
        "ნუცუბიძის ფერდობი":"Saburtalo",
        "ვერა":"Mtatsminda",
        "სოფ. დიღომი":"Didi Dighomi",
        "აეროპორტის დას.":"Samgori",
        "ვაზისუბანი":"Isani",
        "ვარკეთილი":"Samgori",
        "ისანი":"Isani",
        "ლილო":"Samgori",
        "მესამე მასივი":"Samgori",
        "ნავთლუღი":"Isani",
        "ორთაჭალა":"Krtsanisi",
        "ორხევი":"Samgori",
        "სამგორი":"Samgori",
        "ფონიჭალა":"Krtsanisi",
        "აბანოთუბანი":"Krtsanisi",
        "ავლაბარი":"Isani",
        "ელია":"Isani",
        "კრწანისი":"Krtsanisi",
        "მთაწმინდა":"Mtatsminda",
        "სოლოლაკი":"Mtatsminda",
        "მოსკოვის გამზირი":"Samgori",
        "ლისის მიმდებარედ":"Saburtalo",
        "ივერთუბანი":"Chughureti",
        "დიღმის ჭალა":"Didi Dighomi",
        "აფრიკა":"Samgori",
        "გიორგიწმინდას დას.":"Gldani",
    }
    return map_dict[item]

# def urban_drop_check(item):
#     check = item in [0,15,16,17,18,19,20,21,22,102,44,45]
#     return check
def urban_id_check(item):
    check = item in [1,2,3,4,5,6,7,8,9,10,11,12,23,24,25,26,27,28,29,30,38,39,40,42,43,46,47,
                 48,49,51,52,53,54,55,56,57,58,59,60,61,62,63,64,65,66,
                 67,78,101,103,106,117,122]
    return check

def urban_id_map(item):
    map_dict = {
        1:"Gldani",
        2:"Gldani",
        3:"Gldani",
        4:"Gldani",
        5:"Nadzaladevi",
        6:"Nadzaladevi",
        7:"Gldani",
        8:"Nadzaladevi",
        9:"Gldani",
        10:"Nadzaladevi",
        11:"Nadzaladevi",
        12:"Gldani",
        23:"Didube",
        24:"Didube",
        25:"Chughureti",
        26:"Chughureti",
        27:"Chughureti",
        28:"Vake",
        29:"Didi Dighomi",
        30:"Didi Dighomi",
        38:"Vake",
        39:"Vashlijvari",
        40:"Saburtalo",
        #41:"Saburtalo",
        42:"Vake",
        43:"Saburtalo",
        46:"Saburtalo",
        47:"Saburtalo",
        48:"Didi Dighomi",
        49:"Samgori",
        51:"Isani",
        52:"Samgori",
        53:"Isani",
        54:"Samgori",
        55:"Samgori",
        56:"Isani",
        57:"Krtsanisi",
        58:"Samgori",
        59:"Samgori",
        60:"Krtsanisi",
        61:"Krtsanisi",
        62:"Isani",
        63:"Isani",
        64:"Mtatsminda",
        65:"Krtsanisi",
        66:"Mtatsminda",
        67:"Mtatsminda",
        78:"Samgori",
        101:"Saburtalo",
        103:"Chughureti",
        106:"Didi Dighomi",
        117:"Samgori",
        122:"Gldani",
    }
    return map_dict[item]

def should_be_dropped(row):
    if urban_name_drop_check(row['urban_name']):
        return True
    else:
        if urban_name_check(row['urban_name']):
            return False
        else:
            if urban_id_check(row['urban_id']):
                return False
            else:
                return True

def should_use_urban_name(row):
    return urban_name_check(row['urban_name'])

def column_value(row):
    if should_use_urban_name(row):
        value = urban_name_map(row['urban_name'])
    else:
        value = urban_id_map(row['urban_id'])
    return value

def urban_create(df):
    df = df[~df.apply(should_be_dropped, axis=1)].reset_index(drop=True)
    df['urban'] = df.apply(column_value, axis=1)
    return df

def urban_fix(df):
    df = drop_bad_observations(df)
    df = urban_create(df)
    df.drop(['district_name', 'urban_name', 'district_id', 'urban_id'], axis=1, inplace=True)
    return df
