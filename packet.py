# Login_check_URL = "http://cos2.ntnu.edu.tw/AasEnrollStudent/LoginCheckCtrl"
# Rand_image_URL = "http://cos2.ntnu.edu.tw/AasEnrollStudent/RandImage"
# Image_box_URL = "http://cos2.ntnu.edu.tw/AasEnrollStudent/ImageBoxFromIndexCtrl"
# Index_URL = "http://cos2.ntnu.edu.tw/AasEnrollStudent/IndexCtrl"
Login_URL = "http://cos1s.ntnu.edu.tw/AasEnrollStudent/LoginCtrl"
# Enroll_URL = "http://cos2.ntnu.edu.tw/AasEnrollStudent/EnrollCtrl"
# Course_query_URL = "http://cos2.ntnu.edu.tw/AasEnrollStudent/CourseQueryCtrl"
# Stfseld_list_URL = "http://cos2.ntnu.edu.tw/AasEnrollStudent/StfseldListCtrl"

def headers(j_session_id):
    return {
        'sec-ch-ua': '"Google Chrome";v="93", " Not;A Brand";v="99", "Chromium";v="93"',
        'X-Requested-With': 'XMLHttpRequest',
        'sec-ch-ua-mobile': '?0',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 Safari/537.36',
        'sec-ch-ua-platform': '"Windows"',
        'Accept': '*/*',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Dest': 'empty',
        'Cookie': f'JSESSIONID={j_session_id}',
        'referer': '',
    }

# response = requests.request("POST", url, headers=HEADERS, data=payload)

# print(response.text)