import { MapContainer, TileLayer, Marker, Popup } from "react-leaflet"
import L from "leaflet"

interface Props {
  lat: number
  lng: number
  stopName: string
}

const stopIcon = new L.Icon({
  iconUrl: "https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-blue.png",
  shadowUrl: "https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-shadow.png",
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
})

export default function BusStopMap({ lat, lng, stopName }: Props) {
  return (
    <div className="rounded-2xl overflow-hidden shadow-md h-64 w-full">
      <MapContainer center={[lat, lng]} zoom={16} style={{ height: "100%", width: "100%" }}>
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        <Marker position={[lat, lng]} icon={stopIcon}>
          <Popup>{stopName}</Popup>
        </Marker>
      </MapContainer>
    </div>
  )
}
