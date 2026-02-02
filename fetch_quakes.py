import requests
import csv
from datetime import datetime
import warnings

warnings.filterwarnings("ignore", category=requests.packages.urllib3.exceptions.InsecureRequestWarning)

def is_strictly_mainland(lat, lon, place):
    """Filter for Mainland China ONLY - NO border regions, NO other countries."""
    # Taiwan region - always exclude
    if 20.0 <= lat <= 26.5 and 118.0 <= lon <= 123.5:
        return False
    
    place_upper = place.upper() if place else ""
    
    # Exclude ANY record that mentions other countries (even border regions)
    exclude_keywords = ["JAPAN", "RYUKYU", "PHILIPPINES", "TAIWAN", "INDIA", "MYANMAR", 
                        "VIETNAM", "LAOS", "RUSSIA", "MONGOLIA", "KOREA", "PAKISTAN", 
                        "AFGHANISTAN", "KYRGYZSTAN", "KAZAKHSTAN", "TAJIKISTAN", "NEPAL", 
                        "BHUTAN", "BANGLADESH", "THAILAND", "HOKKAIDO", "LUZON", "MINDANAO",
                        "PHILIPPINE", "CELEBES", "BORDER"]
    
    for kw in exclude_keywords:
        if kw in place_upper:
            return False
    
    # China-specific keywords that MUST appear
    china_keywords = ["CHINA", "XINJIANG", "XIZANG", "TIBET", "SICHUAN", "YUNNAN", 
                      "GANSU", "QINGHAI", "SHAANXI", "SHANXI", "HEBEI", "HENAN",
                      "SHANDONG", "JIANGSU", "ZHEJIANG", "ANHUI", "FUJIAN", "JIANGXI",
                      "HUBEI", "HUNAN", "GUANGDONG", "GUANGXI", "HAINAN", "GUIZHOU",
                      "CHONGQING", "LIAONING", "JILIN", "HEILONGJIANG", "INNER MONGOLIA",
                      "NINGXIA", "BEIJING", "SHANGHAI", "TIANJIN"]
    
    # Must contain at least one China keyword
    return any(kw in place_upper for kw in china_keywords)


def fetch_isc_fdsn():
    """Fetch earthquake data from ISC FDSN event service (as used in the literature)."""
    url = "http://www.isc.ac.uk/fdsnws/event/1/query"
    params = {
        "format": "text",
        "starttime": "2015-01-01",
        "endtime": "2025-12-31",
        "minlat": 18, "maxlat": 54,
        "minlon": 73, "maxlon": 135,
        "mindepth": 0, "maxdepth": 5,
        "minmag": 4.5, "maxmag": 6.0
    }
    headers = {'User-Agent': 'Mozilla/5.0'}
    quakes = []
    print("Fetching from ISC FDSN Event Service...")
    
    try:
        resp = requests.get(url, params=params, headers=headers, timeout=120)
        lines = resp.text.strip().split('\n')
        
        for line in lines:
            if line.startswith('#') or not line.strip():
                continue
            
            parts = line.split('|')
            if len(parts) >= 14:
                try:
                    event_id = parts[0]
                    time_str = parts[1]
                    lat = float(parts[2])
                    lon = float(parts[3])
                    depth = float(parts[4]) if parts[4] else 0
                    author = parts[5]
                    mag_type = parts[9] if len(parts) > 9 else "M"
                    magnitude = float(parts[10]) if len(parts) > 10 and parts[10] else 0
                    place = parts[12] if len(parts) > 12 else "ISC Event"
                    
                    # Parse time
                    try:
                        timestamp = datetime.strptime(time_str[:19], "%Y-%m-%dT%H:%M:%S")
                    except:
                        continue
                    
                    # Filter for Mainland China
                    if not is_strictly_mainland(lat, lon, place):
                        continue
                    
                    # Filter for depth 0-5km
                    if depth < 0 or depth > 5:
                        continue
                        
                    # Filter for magnitude 4.5-6.0
                    if magnitude < 4.5 or magnitude > 6.0:
                        continue
                    
                    quakes.append({
                        "source": "ISC",
                        "id": event_id,
                        "time": timestamp,
                        "latitude": lat,
                        "longitude": lon,
                        "magnitude": magnitude,
                        "depth_km": depth,
                        "place": place,
                        "depth_method": f"ISC Reviewed ({author}, {mag_type})"
                    })
                except Exception as e:
                    continue
    except Exception as e:
        print(f"ISC FDSN Error: {e}")
    
    print(f"ISC FDSN: {len(quakes)} events")
    return quakes

def fetch_emsc():
    """Fetch earthquake data from EMSC/Seismic Portal."""
    url = "https://www.seismicportal.eu/fdsnws/event/1/query"
    params = {
        "format": "json",
        "starttime": "2015-01-01",
        "endtime": "2025-12-31",
        "minmag": 4.5, "maxmag": 6.0,
        "minlat": 18, "maxlat": 54,
        "minlon": 73, "maxlon": 135,
        "mindepth": 0, "maxdepth": 5
    }
    headers = {'User-Agent': 'Mozilla/5.0'}
    quakes = []
    print("Fetching from EMSC/Seismic Portal...")
    
    try:
        resp = requests.get(url, params=params, headers=headers, timeout=30)
        data = resp.json()
        for f in data.get("features", []):
            p = f["properties"]
            coords = f["geometry"]["coordinates"]
            lon, lat, depth = coords
            place = p.get("flynn_region", "EMSC Event")
            
            if not is_strictly_mainland(lat, lon, place):
                continue
            
            t_str = p["time"]
            try:
                timestamp = datetime.strptime(t_str, "%Y-%m-%dT%H:%M:%S.%fZ")
            except:
                try:
                    timestamp = datetime.fromisoformat(t_str.replace("Z", "+00:00")).replace(tzinfo=None)
                except:
                    timestamp = datetime.strptime(t_str[:19], "%Y-%m-%dT%H:%M:%S")

            quakes.append({
                "source": "EMSC",
                "id": f["id"],
                "time": timestamp,
                "latitude": lat,
                "longitude": lon,
                "magnitude": p["mag"],
                "depth_km": depth,
                "place": place,
                "depth_method": f"EMSC ({p.get('source_catalog', 'Unknown')})"
            })
    except Exception as e:
        print(f"EMSC Error: {e}")
    
    print(f"EMSC: {len(quakes)} events")
    return quakes

def fetch_usgs():
    """Fetch earthquake data from USGS."""
    url = "https://earthquake.usgs.gov/fdsnws/event/1/query"
    params = {
        "format": "geojson",
        "starttime": "2015-01-01",
        "endtime": "2025-12-31",
        "minmagnitude": 4.5, "maxmagnitude": 6.0,
        "minlatitude": 18, "maxlatitude": 54,
        "minlongitude": 73, "maxlongitude": 135,
        "mindepth": 0, "maxdepth": 5
    }
    headers = {'User-Agent': 'Mozilla/5.0'}
    quakes = []
    print("Fetching from USGS...")
    
    try:
        try:
            resp = requests.get(url, params=params, headers=headers, timeout=30)
        except:
            resp = requests.get(url, params=params, headers=headers, timeout=30, verify=False)
            
        data = resp.json()
        for f in data.get("features", []):
            p = f["properties"]
            coords = f["geometry"]["coordinates"]
            lon, lat, depth = coords
            place = p["place"]
            
            if not is_strictly_mainland(lat, lon, place):
                continue
                
            timestamp = datetime.fromtimestamp(p["time"] / 1000.0)
            quakes.append({
                "source": "USGS",
                "id": f["id"],
                "time": timestamp,
                "latitude": lat,
                "longitude": lon,
                "magnitude": p["mag"],
                "depth_km": depth,
                "place": place,
                "depth_method": "USGS Reviewed" if p["status"] == "reviewed" else "USGS Automatic"
            })
    except Exception as e:
        print(f"USGS Error: {e}")
    
    print(f"USGS: {len(quakes)} events")
    return quakes

def deduplicate(all_quakes):
    """Remove duplicate events based on time and location proximity."""
    if not all_quakes:
        return []
    
    # Sort by time
    all_quakes.sort(key=lambda x: x["time"])
    
    unique_quakes = []
    for q in all_quakes:
        is_duplicate = False
        for u in unique_quakes:
            time_diff = abs((q["time"] - u["time"]).total_seconds())
            dist_diff = ((q["latitude"] - u["latitude"])**2 + (q["longitude"] - u["longitude"])**2)**0.5
            
            if time_diff < 120 and dist_diff < 0.5:
                is_duplicate = True
                # Prefer ISC > USGS > EMSC for source priority (based on literature)
                if q["source"] == "ISC":
                    u.update(q)
                elif q["source"] == "USGS" and u["source"] == "EMSC":
                    u.update(q)
                break
        if not is_duplicate:
            unique_quakes.append(q)
    return unique_quakes

def main():
    print("="*60)
    print("Seismic Catalog Generation - Literature-Based Data Sources")
    print("Data sources: ISC (CENC contributed), EMSC, USGS")
    print("="*60)
    
    # Fetch from multiple sources (as mentioned in Lei et al. papers)
    # ISC is the primary source as it includes CENC contributions
    isc_data = fetch_isc_fdsn()
    emsc_data = fetch_emsc()
    usgs_data = fetch_usgs()
    
    all_data = isc_data + emsc_data + usgs_data
    print(f"\nTotal raw records from all sources: {len(all_data)}")
    
    # Deduplicate
    unique_data = deduplicate(all_data)
    print(f"After de-duplication: {len(unique_data)}")
    
    # Sort by time
    unique_data.sort(key=lambda x: x["time"])
    
    # Save to CSV
    csv_file = "china_quakes.csv"
    keys = ["id", "time", "latitude", "longitude", "magnitude", "depth_km", "place", "depth_method", "source"]
    with open(csv_file, 'w', newline='', encoding='utf-8') as f:
        dict_writer = csv.DictWriter(f, fieldnames=keys)
        dict_writer.writeheader()
        for row in unique_data:
            out_row = row.copy()
            out_row["time"] = row["time"].strftime('%Y-%m-%d %H:%M:%S')
            # Standardize depth to positive 0-5km
            out_row["depth_km"] = min(max(abs(row["depth_km"]), 0), 5)
            dict_writer.writerow(out_row)

    
    print(f"\n✓ Saved {len(unique_data)} records to {csv_file}")
    print("="*60)

if __name__ == "__main__":
    main()
