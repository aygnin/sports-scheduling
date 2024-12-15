import os
import googlemaps

maps_client = googlemaps.Client(os.environ["MAPS_API_KEY"])

num_unis = 15
uni_ids = {
    0: "Queens", 1: "Western", 2: "Waterloo", 3: "Brock", 4: "Windsor", 5: "McMaster",
    6: "Lakehead", 7: "Toronto", 8: "York", 9: "Ottawa", 10: "Toronto Metropolitan", 11: "Nipissing",
    12: "Guelph", 13: "RMC", 14: "Trent"
}
uni_to_stadium = {
    "Queens": "284 Earl St, Kingston, ON K7L 3N6",
    "Western": "Alumni Hall, Lambton Dr, London, ON N6G 1G8",
    "Waterloo": "Physical Activities Complex, 200 University Ave W, Waterloo, ON N2L 3G1",
    "Brock": "1812 Sir Isaac Brock Way, St. Catharines, ON L2S 3A1",
    "Windsor": "2555 College Ave, Windsor, ON N9B 3P4",
    "McMaster": "1280 Main St W, Hamilton, ON L8S 4E4",
    "Lakehead": "955 Sanders Dr, Thunder Bay, ON P7B 5E1",
    "Toronto": "100 Devonshire Pl, Toronto, ON M5S 2C9",
    "York": "1 Thompson Rd, North York, ON M3J 1P3",
    "Ottawa": "125 University Private, Ottawa, ON, Canada",
    "Toronto Metropolitan": "50 Carlton St., Toronto, ON M5B 1J2",
    "Nipissing": "100 College Dr, North Bay, ON P1B 0A4",
    "Guelph": "50 E Ring Rd, Guelph, ON N1G 4Z8",
    "RMC": "11 Navy Way, Kingston, ON K7K 7B4",
    "Trent": "1650 W Bank Dr, Peterborough, ON K9L 1Z7"
}

assert (num_unis == len(uni_to_stadium))

# distances in kilometres
distance_matrix = [[0] * num_unis for _ in range(num_unis)]

for i in range(num_unis):
    for j in range(0, num_unis, 3):
        distances = maps_client.distance_matrix(
            uni_to_stadium[uni_ids[i]], 
            [uni_to_stadium[u] for u in [uni_ids[t] for t in range(j, j+3)]]
        )

        # parsing distances structure as given in 
        # https://developers.google.com/maps/documentation/distance-matrix/distance-matrix#distance-matrix-responses
        
        for k in range(len(distances["rows"][0]["elements"])):
            entry = distances["rows"][0]["elements"][k]

            [dist, unit] = entry["distance"]["text"].replace(",", "").split()
            dist = float(dist)
    
            if unit == "m":
                dist *= 0.001
            
            distance_matrix[i][j + k] = dist

for i in range(num_unis):
    with open("distances.txt", "w") as file:
        print(", ".join(distance_matrix[i]))