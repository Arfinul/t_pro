#----------------------------------------------------------------
# Generated CMake target import file.
#----------------------------------------------------------------

# Commands may need to know the format version.
set(CMAKE_IMPORT_FILE_VERSION 1)

# Import target "Darknet::dark" for configuration ""
set_property(TARGET Darknet::dark APPEND PROPERTY IMPORTED_CONFIGURATIONS NOCONFIG)
set_target_properties(Darknet::dark PROPERTIES
  IMPORTED_LINK_DEPENDENT_LIBRARIES_NOCONFIG "opencv_calib3d;opencv_core;opencv_dnn;opencv_features2d;opencv_flann;opencv_gapi;opencv_highgui;opencv_imgcodecs;opencv_imgproc;opencv_ml;opencv_objdetect;opencv_photo;opencv_stitching;opencv_video;opencv_videoio"
  IMPORTED_LOCATION_NOCONFIG "/home/amc012/Music/flc_without_ref/libdark.so"
  IMPORTED_SONAME_NOCONFIG "libdark.so"
  )

list(APPEND _IMPORT_CHECK_TARGETS Darknet::dark )
list(APPEND _IMPORT_CHECK_FILES_FOR_Darknet::dark "/home/amc012/Music/flc_without_ref/libdark.so" )

# Commands beyond this point should not need to know the version.
set(CMAKE_IMPORT_FILE_VERSION)
