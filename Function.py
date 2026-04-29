import geopandas as gpd
from shapely.ops import voronoi_diagram
from shapely.geometry import MultiPoint
from shapely import union_all


def no_overlap(polygons: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """
    Split overlapping polygon catchments by assigning overlap areas to the
    nearest polygon centroid using a Voronoi tessellation.

    Parameters
    ----------
    polygons : geopandas.GeoDataFrame
        Input polygon GeoDataFrame.

    Returns
    -------
    geopandas.GeoDataFrame
        GeoDataFrame with original attributes, but geometries clipped to
        centroid-based Voronoi cells so they no longer overlap.
    """

    # Use representative points if you want guaranteed points inside polygons.
    # To match the R function exactly, use centroids.
    centroids = polygons.copy()
    centroids["geometry"] = polygons.geometry.centroid

    # Create Voronoi polygons from centroid locations
    multipoint = MultiPoint(list(centroids.geometry))
    vor = voronoi_diagram(multipoint, envelope=polygons.unary_union.envelope)

    voronoi = list(vor.geoms)

    # Put Voronoi polygons back in the same order as the input centroids
    ordered_voronoi = []

    for point in centroids.geometry:
        matches = [cell for cell in voronoi if cell.intersects(point)]

        if len(matches) == 0:
            ordered_voronoi.append(None)
        else:
            ordered_voronoi.append(matches[0])

    # Keep original attributes, but replace geometry
    result = polygons.copy()

    new_geometries = []

    for poly, cell in zip(polygons.geometry, ordered_voronoi):
        if cell is None:
            new_geometries.append(poly)
        else:
            clipped = poly.intersection(cell)

            # Equivalent to st_union() in case intersection creates multipart pieces
            if hasattr(clipped, "geoms"):
                clipped = union_all(list(clipped.geoms))

            new_geometries.append(clipped)

    result = result.set_geometry(new_geometries)
    result = result.set_crs(polygons.crs, allow_override=True)

    return result
