import type {
  GeometryData,
  PolygonCoordinates,
  Position,
} from '../types'

export interface Projection {
  project: (position: Position) => Position
  width: number
  height: number
}

export function createProjection(
  geometry: GeometryData,
  width = 720,
  height = 430,
  padding = 14,
): Projection {
  const positions: Position[] = []
  for (const feature of geometry.features) {
    const polygons =
      feature.geometry.type === 'Polygon'
        ? [feature.geometry.coordinates]
        : feature.geometry.coordinates
    for (const polygon of polygons) {
      for (const ring of polygon) positions.push(...ring)
    }
  }
  const longitudes = positions.map(([longitude]) => longitude)
  const latitudes = positions.map(([, latitude]) => latitude)
  const minLongitude = Math.min(...longitudes)
  const maxLongitude = Math.max(...longitudes)
  const minLatitude = Math.min(...latitudes)
  const maxLatitude = Math.max(...latitudes)
  const scale = Math.min(
    (width - padding * 2) / (maxLongitude - minLongitude),
    (height - padding * 2) / (maxLatitude - minLatitude),
  )
  const mapWidth = (maxLongitude - minLongitude) * scale
  const mapHeight = (maxLatitude - minLatitude) * scale
  const offsetX = (width - mapWidth) / 2
  const offsetY = (height - mapHeight) / 2
  return {
    width,
    height,
    project: ([longitude, latitude]) => [
      offsetX + (longitude - minLongitude) * scale,
      offsetY + (maxLatitude - latitude) * scale,
    ],
  }
}

export function featurePath(
  geometry: GeometryData,
  featureIndex: number,
  projection: Projection,
): string {
  const feature = geometry.features[featureIndex]
  const polygons =
    feature.geometry.type === 'Polygon'
      ? [feature.geometry.coordinates]
      : feature.geometry.coordinates
  return polygons
    .map((polygon) => polygonPath(polygon, projection))
    .join(' ')
}

function polygonPath(
  polygon: PolygonCoordinates,
  projection: Projection,
): string {
  return polygon
    .map((ring) =>
      ring
        .map((position, index) => {
          const [x, y] = projection.project(position)
          return `${index === 0 ? 'M' : 'L'}${x.toFixed(2)},${y.toFixed(2)}`
        })
        .join(' ') + ' Z',
    )
    .join(' ')
}
