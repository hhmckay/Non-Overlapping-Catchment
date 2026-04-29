# Unique station catchment function
# https://gis.stackexchange.com/questions/358797/splitting-overlap-between-polygons-and-assign-to-nearest-polygon-using-r
st_no_overlap <- function(polygons) {
  
  centroids <- polygons %>% st_centroid
  
  # Voronoi tesselation
  voronoi <- 
    centroids %>% 
    st_geometry() %>%
    st_union() %>%
    st_voronoi() %>%
    st_collection_extract() # now it's sfc
  
  # Put them back in their original order
  voronoi <-
    voronoi[unlist(st_intersects(centroids,voronoi))]
  
  # Keep the attributes
  result <- centroids
  
  st_geometry(result) <-
    mapply(
      function(x,y) {
        z <- 
          st_intersection(
            x,
            y
          ) %>% 
          # this can create multiple parts, so we union.
          st_union()
      },
      # we need this to produce a list to iterate over
      # in parallel with voronoi elements, so we 
      # convert to sfc
      st_as_sfc(polygons[attributes(polygons)$sf_column]),
      voronoi,
      SIMPLIFY=FALSE
    ) %>% 
    # st_sfc() returned errors, but st_as_sfc() did not
    st_as_sfc(crs = st_crs(centroids))
  
  result
}
