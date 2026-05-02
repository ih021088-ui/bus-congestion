import { MapContainer, TileLayer, Marker, Popup } from "react-leaflet"
import L from "leaflet"

// 수원대학교 7790 정류장 좌표
const STOP_LAT = 37.2378
const STOP_LNG = 126.9301

const stopIcon = new L.Icon({
  iconUrl: "https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-blue.png",
  shadowUrl: "https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-shadow.png",
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
})

export default function BusStopMap() {
  return (
    <div className="rounded-2xl overflow-hidden shadow-md h-64 w-full">
      <MapContainer center={[STOP_LAT, STOP_LNG]} zoom={16} style={{ height: "100%", width: "100%" }}>
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        <Marker position={[STOP_LAT, STOP_LNG]} icon={stopIcon}>
          <Popup>수원대학교 버스정류장 (7790)</Popup>
        </Marker>
      </MapContainer>
    </div>
  )
}
