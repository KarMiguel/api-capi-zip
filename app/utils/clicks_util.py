import requests

def get_location_from_ip(ip):
    response = requests.get(f"https://ipinfo.io/{ip}/geo")

    if response.status_code == 200:
        data = response.json()
        
        city = data.get('city')
        region = data.get('region')
        country = data.get('country')
    
        if city:
            return f"{city} / {region} - {country} "
        else:
            "Localização não encontrada."
    else:
        "Error"


def get_from_ip():
    response = requests.get('https://api.ipify.org/')
    
    if response.status_code == 200:
        return response.text
    else:
        return "Ip não localizado"
