import json

def data_load(path):
    with open(path, 'r') as file:
        # Parse the JSON data
        data = json.load(file)
    return data

def nearby_places_extract(nearby_places):
    if nearby_places:
        school = nearby_places["სკოლა"]["nearby_places"]
        miscellaneous = nearby_places['სხვადასხვა']['nearby_places']
        shop_food = nearby_places['მაღაზია / კვება']['nearby_places']
        fitness = nearby_places['აფთიაქი']['nearby_places']
        apothecary = nearby_places['აფთიაქი']['nearby_places']
    else:
        school = []
        miscellaneous = []
        shop_food = []
        fitness = []
        apothecary = []

    modified_nearby_places = {
        "school_features": list(nearby_places_feature_grab(school)),
        "miscellaneous_features": list(nearby_places_feature_grab(miscellaneous)),
        "shop_features": list(nearby_places_feature_grab(shop_food)),
        "fitness_features": list(nearby_places_feature_grab(fitness)),
        "apothecary_features": list(nearby_places_feature_grab(apothecary)),
    }

    return modified_nearby_places

def nearby_places_feature_grab(place):
    name = []
    lat = []
    lng = []
    distance = []
    for item in place:
        name.append(item['name'])
        lat.append(item['lat'])
        lng.append(item['lng'])
        distance.append(item['distance'])
    return name,lat,lng,distance

def image_collector(images):
    large = []
    blur = []
    thumb = []
    for image in images:
        large.append(image['large'])
        blur.append(image['blur'])
        thumb.append(image['thumb'])
    return large, blur, thumb

def parameter_check(parameters):
    ids = []
    for parameter in parameters:
        ids.append(parameter['id'])
    has_parameter = []
    for i in range(54):
        if (i+1) in ids:
            has_parameter.append(True)
        else:
            has_parameter.append(False)
    return has_parameter


def row_creator(item, mapping):
    main_data = item["main_data"]
    nearby_places = nearby_places_extract(main_data['nearby_places'])
    large, blur, thumb  = image_collector(main_data['images'])

    parameters = main_data['parameters']
    has_parameter = parameter_check(parameters)

    if main_data['bathroom_type_id']:
        bathroom_type = mapping["bathroom_types"][str(main_data['bathroom_type_id'])]
    else:
        bathroom_type = None

    if main_data['lease_type_id']:
        lease_type = mapping["lease_types"][str(main_data["lease_type_id"])]
    else:
        lease_type = None

    try:
        user_type = main_data["user_type"]["type"]
    except KeyError:
        user_type = None

    if main_data['heating_type_id']:
        heating_type = mapping["heating_types"][str(main_data["heating_type_id"])]
    else:
        heating_type = None

    if main_data["material_type_id"]:
        material_type = mapping["material_types"][str(main_data["material_type_id"])]
    else:
        material_type = None

    if main_data['parking_type_id']:
        parking_type = mapping["parking_types"][str(main_data["parking_type_id"])]
    else:
        parking_type = None

    if main_data['project_type_id']:
        project_type = mapping["project_types"][str(main_data["project_type_id"])]
    else:
        project_type = None

    if main_data['storeroom_type_id']:
        storeroom_type = mapping["storeroom_types"][str(main_data["storeroom_type_id"])]
    else:
        storeroom_type = None

    row = {
        "data_update_count": item["data_update_count"],
        "id": main_data["id"],
        "uuid": main_data["uuid"],
        "price_1_price_total": main_data["price"]["1"]["price_total"],
        "price_1_price_square": main_data["price"]["1"]["price_square"],
        "price_2_price_total": main_data["price"]["2"]["price_total"],
        "price_2_price_square": main_data["price"]["2"]["price_square"],
        "price_3_price_total": main_data["price"]["3"]["price_total"],
        "price_3_price_square": main_data["price"]["3"]["price_square"],
        "condition_id": main_data['condition_id'],
        "deal_type_id": main_data['deal_type_id'],
        "real_estate_type_id": main_data['real_estate_type_id'],
        "city_id": main_data['city_id'],
        "total_price": main_data['total_price'],
        "city_name": main_data['city_name'],
        "district_id": main_data['district_id'],
        "district_name": main_data['district_name'],
        "urban_id": main_data['urban_id'],
        "urban_name": main_data['urban_name'],
        "status_id": main_data['status_id'],
        "estate_status_types": mapping["estate_status_types"][str(main_data['status_id'])],
        "room_type_id": main_data['room_type_id'],
        "published": main_data['published'],
        "bedroom_type_id": main_data['bedroom_type_id'],
        "bathroom_type_id": main_data['bathroom_type_id'],
        "bathroom_type": bathroom_type,
        "project_type_id": main_data['project_type_id'],
        "project_type": project_type,
        "project_id": main_data['project_id'],
        "project_uuid": main_data['project_uuid'],
        "hot_water_type_id": main_data['hot_water_type_id'],
        "heating_type_id": main_data['heating_type_id'],
        "heating_type": heating_type,
        "parking_type_id": main_data['parking_type_id'],
        "parking_type": parking_type,
        "height": main_data['height'],
        "balconies": main_data['balconies'],
        "balcony_area": main_data['balcony_area'],
        "lat": main_data['lat'],
        "lng": main_data['lng'],
        "storeroom_type_id": main_data['storeroom_type_id'],
        "storeroom_type": storeroom_type,
        "material_type_id": main_data['material_type_id'],
        "material_type": material_type,
        "3d_url": main_data['3d_url'],
        "youtube_link": main_data['youtube_link'],
        "address": main_data['address'],
        "comment": main_data['comment'],
        "last_updated": main_data['last_updated'],
        "created_at": main_data['created_at'],
        "area": main_data['area'],
        "area_type_id": main_data['area_type_id'],
        "floor": main_data['floor'],
        "total_floors": main_data['total_floors'],
        "views": main_data['views'],
        "rating": main_data['rating'],
        "owner_name": main_data['owner_name'],
        "user_phone_number": main_data['user_phone_number'],
        "gifts": main_data['gifts'],
        "favorite": main_data['favorite'],
        "is_old": main_data['is_old'],
        "price_negotiable": main_data['price_negotiable'],
        "price_from": main_data['price_from'],
        "yard_area": main_data['yard_area'],
        "is_owner": main_data['is_owner'],
        "map_static_image": main_data['map_static_image'],
        "all_nearby_places_image": main_data['all_nearby_places_image'],
        "school_name": nearby_places["school_features"][0],
        "school_lat": nearby_places["school_features"][1],
        "school_lng": nearby_places["school_features"][2],
        "school_distance": nearby_places["school_features"][3],
        "miscellaneous_name": nearby_places["miscellaneous_features"][0],
        "miscellaneous_lat": nearby_places["miscellaneous_features"][1],
        "miscellaneous_lng": nearby_places["miscellaneous_features"][2],
        "miscellaneous_distance": nearby_places["miscellaneous_features"][3],
        "shop_name": nearby_places["shop_features"][0],
        "shop_lat": nearby_places["shop_features"][1],
        "shop_lng": nearby_places["shop_features"][2],
        "shop_distance": nearby_places["shop_features"][3],
        "fitness_name": nearby_places["fitness_features"][0],
        "fitness_lat": nearby_places["fitness_features"][1],
        "fitness_lng": nearby_places["fitness_features"][2],
        "fitness_distance": nearby_places["fitness_features"][3],
        "apothecary_name": nearby_places["apothecary_features"][0],
        "apothecary_lat": nearby_places["apothecary_features"][1],
        "apothecary_lng": nearby_places["apothecary_features"][2],
        "apothecary_distance": nearby_places["apothecary_features"][3],
        "dynamic_title": main_data["dynamic_title"],
        "dynamic_slug": main_data["dynamic_slug"],
        "is_active": main_data["is_active"],
        "rs_code": main_data["rs_code"],
        "appear_rs_code": main_data["appear_rs_code"],
        "can_exchanged": main_data["can_exchanged"],
        "can_exchanged_comment": main_data["can_exchanged_comment"],
        "for_special_people": main_data["for_special_people"],
        "lease_period": main_data["lease_period"],
        "lease_type_id": main_data["lease_type_id"],
        "lease_type": lease_type,
        "lease_contract_type_id": main_data["lease_contract_type_id"],
        "rent_period": main_data["rent_period"],
        "rent_type_id": main_data["rent_type_id"],
        "daily_rent_type_id": main_data["daily_rent_type_id"],
        "daily_rent_type": main_data["daily_rent_type"],
        "storeroom_area": main_data["storeroom_area"],
        "swimming_pool_type": main_data["swimming_pool_type"],
        "hot_water_type": main_data["hot_water_type"],
        "condition": main_data["condition"],
        "living_room_type": main_data["living_room_type"],
        "build_year": main_data["build_year"],
        "living_room_area": main_data["living_room_area"],
        "loggia_area": main_data["loggia_area"],
        "porch_area": main_data["porch_area"],
        "waiting_space_area": main_data["waiting_space_area"],
        "street_id": main_data["street_id"],
        "point_coordinates": main_data["point"]["coordinates"],
        "currency_id": main_data["currency_id"],
        "price_type_id": main_data["price_type_id"],
        "user_statements_count": main_data["user_statements_count"],
        "user_id": main_data["user_id"],
        "metro_station": main_data["metro_station"],
        "has_color": main_data["has_color"],
        "is_vip": main_data["is_vip"],
        "is_vip_plus": main_data["is_vip_plus"],
        "is_super_vip": main_data["is_super_vip"],
        "grouped_street_id": main_data["grouped_street_id"],
        "price_label": main_data["price_label"],
        "has_gas": has_parameter[0],
        "has_internet":has_parameter[1],
        "has_TV":has_parameter[2],
        "has_air_conditioner":has_parameter[3],
        "has_alarms": has_parameter[4],
        "has_elevator":has_parameter[5],
        "has_ventilation":has_parameter[6],
        "has_freight_elevator":has_parameter[7],
        "has_chimney":has_parameter[8],
        "has_furniture":has_parameter[9],
        "has_telephone":has_parameter[10],
        "has_protection":has_parameter[11],
        "has_Jacuzzi":has_parameter[12],
        "has_swimming_pool":has_parameter[13],
        "has_sauna":has_parameter[14],
        "has_fridge":has_parameter[15],
        "has_washing_machine":has_parameter[16],
        "has_dishwasher":has_parameter[17],
        "has_stove":has_parameter[18],
        "has_oven":has_parameter[19],
        "has_living_room":has_parameter[20],
        "has_loggia":has_parameter[21],
        "has_veranda":has_parameter[22],
        "has_water":has_parameter[23],
        "has_sewage":has_parameter[24],
        "has_electricity":has_parameter[25],
        "has_asphalt_road":has_parameter[26],
        "can_be_divided_28":has_parameter[27],
        "with_building":has_parameter[28],
        "with_approved_project_30":has_parameter[29],
        "has_waiting_space": has_parameter[30],
        "has_spa":has_parameter[31],
        "has_cellar":has_parameter[32],
        "has_bar":has_parameter[33],
        "has_gym":has_parameter[34],
        "has_coded_door":has_parameter[35],
        "is_fenced":has_parameter[36],
        "has_gate":has_parameter[37],
        "has_fruit_trees":has_parameter[38],
        "has_grill":has_parameter[39],
        "has_yard_lighting":has_parameter[40],
        "has_yard":has_parameter[41],
        "has_bed":has_parameter[42],
        "has_sofa":has_parameter[43],
        "has_table":has_parameter[44],
        "has_chair":has_parameter[45],
        "has_kitchen_with_technology":has_parameter[46],
        "for_party":has_parameter[47],
        "allows_pets":has_parameter[48],
        "has_storage_room":has_parameter[49],
        "Booking/AirBnb account":has_parameter[50],
        "for_investment":has_parameter[51],
        "with_approved_project_53":has_parameter[52],
        "can_be_divided_54":has_parameter[53],
        "images_large": large,
        "images_blur": blur,
        "images_thumb": thumb,
        "airbnb_link": main_data["airbnb_link"],
        "booking_link": main_data["booking_link"],
        "user_type": user_type,
        "additional_information": main_data["additional_information"],
    }

    return row