## Venue Detail

Production Server : http://54.183.205.145/v1/venues/object_id

Test Server : http://54.153.93.204:9999/v1/venues/object_id

해당 Venue에 대한 상세한 정보를 돌려줍니다. 여기에는 Venue의 Meta정보, 각 요소들의 수치화된 정보들이 담겨있습니다.

Title | Title
------| -----
**HTTP Method** | GET


### Parameters

Parameter | Example | Description
------| ----- | -----
**object_id** | 153701 | **required** ID of venue to retrieve


### Response


✓ = always in response, ○ = sometimes in response


Field | Description | Response Status
------| ----- | -----
**meta** | *name*, *category*, *address*, *phone_number*, *yelp_id*, *yelp_url*, *location* | ✓
**doc_count** | *total_doc* | ✓
**overall** | *positive*, *negative* | ✓
**image** | *url* | ✓
**keyword** | *rank*, *keyword*, *count*, *related* | ✓
**meal_type** | *breakfast*, *brunch*, *lunch*, *dinner*, *dessert* | ✓
**dietary** | *vegan*, *vegetarian*, *gluten_free* | ✓
**venue_preference** | *wait*, *noise*, *family*, *view* | ✓


**Production Server**

[**Try It Out**](http://54.183.205.145/v1/venues/153701)

**Test Server**

[**Try It Out**](http://54.153.93.204:9999/v1/venues/153701)



## Search Venues

Production Server : http://54.183.205.145/v1/venues/search

Test Server : http://54.153.93.204:9999/v1/venues/search


특정 지역 또는 특정 영역의 두 좌표 값(좌측 상단, 우측 하단) 내의 Venue 리스트를 돌려줍니다. Search Query는 Optional 입니다.

**여기에서 돌려주는 Venues의 리스트는 Consento Top Rank 기준입니다.**

Title | Title
------| -----
**HTTP Method** | GET



### Parameters

Parameter | Example | Description
------| ----- | -----
**latlng** | 37.756, -122.454, 37.856, -122.354 | **required** unless *location* is provided.
**location** | San Francisco, CA | **required** unless *latlng* is provided.
**query** | pizza | A search term to be applied against venue names.



### Response

**요청시 Parameter로 Query를 입력했다면, 아래의 각 필드들은 리스트 형태로 각각 and_query, or_query에 담겨져서 리턴됩니다.**

✓ = always in response, ○ = sometimes in response


Field | Description | Response Status
------| ----- | -----
**object_id** | A unique string identifier for this venue. | ✓
**name** | A name of this venue. | ✓
**address** | A street address. | ✓
**location** | Latitude, longitude of this veunue. | ✓
**category** | A category that have been applied to this venue. | ✓
**total_count** | Total count of reviews this venue. | ✓
**doc_count** | Doc count. | ✓
**positive_comments** | Positive Comments. | ✓
**negative_comments** | Negative Comments. | ✓
**pos_rate** | Positive Rate. | ✓


**Production Server**

Using Latitude & Longitude : [**Try It Out**](http://54.183.205.145/v1/venues/search?latlng=37.7577,-122.4376,37.856,-122.354)

Using Location : [**Try It Out**](http://54.183.205.145/v1/venues/search?location=San+Jose,CA)

**Test Server**

Using Latitude & Logitude : [**Try It Out**](http://54.153.93.204:9999/v1/venues/search?latlng=37.7577,-122.4376,37.856,-122.354)

Using Location : [**Try It Out**](http://54.153.93.204:9999/v1/venues/search?location=San+Jose,%20CA)


## Home

Production Server : http://54.183.205.145/v1/venues/**home**

Test Server : http://54.153.93.204:9999/v1/venues/**home**


특정 지역 또는 특정 영역의 두 좌표 값(좌측 상단, 우측 하단) 기준으로 주요 키워드와 추천 Venue 리스트를 돌려줍니다.

**좌표값을 사용 할 경우, Location을 함께 입력해야 합니다.**

Title | Title
------| -----
**HTTP Method** | GET


### Parameters

Parameter | Example | Description
------| ----- | -----
**latlng** | 37.756, -122.454, 37.856, -122.354 | If using lat and long, location is required.
**location** | San Francisco, CA | **required** unless *latlng* is provided.


### Response

✓ = always in response, ○ = sometimes in response

Field | Description | Response Status
------| ----- | -----
**keyword** | *rank*, *keyword*, *related* | ✓
**venue** | *name*, *category*, *address*, *keyword*, *image* | ✓


**Production Server**

Using Latitude & Longitude : [**Try It Out**](http://54.183.205.145/v1/venues/home?latlng=37.7577,-122.4376,37.7688,-122.4487)

Using Location : [**Try It Out**](http://54.183.205.145/v1/venues/home?location=San+Jose,CA)

**Test Server**

Using Latitude & Longitude : [**Try It Out**](http://54.153.93.204:9999/v1/venues/home?latlng=37.7577,-122.4376,37.7688,-122.4487)

Using Location : [**Try It Out**](http://54.153.93.204:9999/v1/venues/home?location=San+Jose,%20CA)

## Recommended Keyword

Production Server : http://54.183.205.145/v1/venues/recommended_keyword

Test Server : http://54.153.93.204:9999/v1/venues/recommended_keyword

특정 지역 또는 특정 영역의 두 좌표 값(좌측 상단, 우측 하단) 기준으로 추천 키워드를 돌려줍니다.

**좌표 값을 사용 할 경우, Location을 함께 입력해야 합니다.**

Title | Title
------| -----
**HTTP Method** | GET


### Parameters

Parameter | Example | Description
------| ----- | -----
**latlng** | 37.756, -122.454, 37.856, -122.354 | If using lat and long, location is required.
**location** | San Francisco, CA | **required** unless *latlng* is provided.


### Response

✓ = always in response, ○ = sometimes in response

Field | Description | Response Status
------| ----- | -----
**keyword** | *rank*, *keyword* | ✓


**Production Server**

Using Latitude & Longitude : [**Try It Out**](http://54.183.205.145/v1/venues/recommended_keyword?latlng=37.7577,-122.4376,37.7688,-122.4487)

Using Location : [**Try It Out**](http://54.183.205.145/v1/venues/recommended_keyword?location=San+Jose,CA)

**Test Server**

Using Latitude & Longitude : [**Try It Out**](http://54.153.93.204:9999/v1/venues/recommended_keyword?latlng=37.7577,-122.4376,37.7688,-122.4487)

Using Location : [**Try It Out**](http://54.153.93.204:9999/v1/venues/recommended_keyword?location=San+Jose,%20CA)


## Related Keyword

Production Server : http://54.183.205.145/v1/venues/related_keyword

Test Server : http://54.153.93.204:9999/v1/venues/related_keyword

특정 키워드를 입력하면, 지역 또는 영역의 두 좌표 값(좌측 상단, 우측 하단) 기준으로 관련 키워드를 돌려줍니다.

**좌표 값을 사용 할 경우, Location을 함께 입력해야 합니다.**

Title | Title
------| -----
**HTTP Method** | GET


### Parameters

Parameter | Example | Description
------| ----- | -----
**latlng** | 37.756, -122.454, 37.856, -122.354 | If using lat and long, location is required.
**location** | San Francisco, CA | **required** unless *latlng* is provided.
**keyword** | Spicy | **required** A search keyword to get related keywords.


### Response

✓ = always in response, ○ = sometimes in response

Field | Description | Response Status
------| ----- | -----
**keyword** | *rank*, *keyword* | ✓


**Production Server**

Using Latitude & Longitude : [**Try It Out**](http://54.183.205.145/v1/venues/related_keyword?keyword=spicy&latlng=37.7577,-122.4376,37.7688,-122.4487&keyword=noodle)

Using Location : [**Try It Out**](http://54.183.205.145/v1/venues/related_keyword?keyword=spicy&location=San+Jose,CA&keyword=noodle)

**Test Server**

Using Latitude & Longitude : [**Try It Out**](http://54.153.93.204:9999/v1/venues/related_keyword?keyword=spicy&latlng=37.7577,-122.4376,37.7688,-122.4487&keyword=noodle)

Using Location : [**Try It Out**](http://54.153.93.204:9999/v1/venues/related_keyword?keyword=spicy&location=San+Jose,%20CA&keyword=noodle)
