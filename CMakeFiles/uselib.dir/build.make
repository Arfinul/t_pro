# CMAKE generated file: DO NOT EDIT!
# Generated by "Unix Makefiles" Generator, CMake Version 3.19

# Delete rule output on recipe failure.
.DELETE_ON_ERROR:


#=============================================================================
# Special targets provided by cmake.

# Disable implicit rules so canonical targets will work.
.SUFFIXES:


# Disable VCS-based implicit rules.
% : %,v


# Disable VCS-based implicit rules.
% : RCS/%


# Disable VCS-based implicit rules.
% : RCS/%,v


# Disable VCS-based implicit rules.
% : SCCS/s.%


# Disable VCS-based implicit rules.
% : s.%


.SUFFIXES: .hpux_make_needs_suffix_list


# Produce verbose output by default.
VERBOSE = 1

# Command-line flag to silence nested $(MAKE).
$(VERBOSE)MAKESILENT = -s

#Suppress display of executed commands.
$(VERBOSE).SILENT:

# A target that is always out of date.
cmake_force:

.PHONY : cmake_force

#=============================================================================
# Set environment variables for the build.

# The shell in which to execute make rules.
SHELL = /bin/sh

# The CMake executable.
CMAKE_COMMAND = /opt/cmake-3.19.8-Linux-aarch64/bin/cmake

# The command to remove a file.
RM = /opt/cmake-3.19.8-Linux-aarch64/bin/cmake -E rm -f

# Escaping for special characters.
EQUALS = =

# The top-level source directory on which CMake was run.
CMAKE_SOURCE_DIR = /home/agnext/Desktop/darknet

# The top-level build directory on which CMake was run.
CMAKE_BINARY_DIR = /home/agnext/Desktop/darknet

# Include any dependencies generated for this target.
include CMakeFiles/uselib.dir/depend.make

# Include the progress variables for this target.
include CMakeFiles/uselib.dir/progress.make

# Include the compile flags for this target's objects.
include CMakeFiles/uselib.dir/flags.make

CMakeFiles/uselib.dir/src/yolo_console_dll.cpp.o: CMakeFiles/uselib.dir/flags.make
CMakeFiles/uselib.dir/src/yolo_console_dll.cpp.o: src/yolo_console_dll.cpp
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --green --progress-dir=/home/agnext/Desktop/darknet/CMakeFiles --progress-num=$(CMAKE_PROGRESS_1) "Building CXX object CMakeFiles/uselib.dir/src/yolo_console_dll.cpp.o"
	/usr/bin/c++ $(CXX_DEFINES) $(CXX_INCLUDES) $(CXX_FLAGS) -o CMakeFiles/uselib.dir/src/yolo_console_dll.cpp.o -c /home/agnext/Desktop/darknet/src/yolo_console_dll.cpp

CMakeFiles/uselib.dir/src/yolo_console_dll.cpp.i: cmake_force
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --green "Preprocessing CXX source to CMakeFiles/uselib.dir/src/yolo_console_dll.cpp.i"
	/usr/bin/c++ $(CXX_DEFINES) $(CXX_INCLUDES) $(CXX_FLAGS) -E /home/agnext/Desktop/darknet/src/yolo_console_dll.cpp > CMakeFiles/uselib.dir/src/yolo_console_dll.cpp.i

CMakeFiles/uselib.dir/src/yolo_console_dll.cpp.s: cmake_force
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --green "Compiling CXX source to assembly CMakeFiles/uselib.dir/src/yolo_console_dll.cpp.s"
	/usr/bin/c++ $(CXX_DEFINES) $(CXX_INCLUDES) $(CXX_FLAGS) -S /home/agnext/Desktop/darknet/src/yolo_console_dll.cpp -o CMakeFiles/uselib.dir/src/yolo_console_dll.cpp.s

# Object files for target uselib
uselib_OBJECTS = \
"CMakeFiles/uselib.dir/src/yolo_console_dll.cpp.o"

# External object files for target uselib
uselib_EXTERNAL_OBJECTS =

uselib: CMakeFiles/uselib.dir/src/yolo_console_dll.cpp.o
uselib: CMakeFiles/uselib.dir/build.make
uselib: libdarknet.so
uselib: /usr/lib/aarch64-linux-gnu/libopencv_dnn.so.4.1.1
uselib: /usr/lib/aarch64-linux-gnu/libopencv_gapi.so.4.1.1
uselib: /usr/lib/aarch64-linux-gnu/libopencv_highgui.so.4.1.1
uselib: /usr/lib/aarch64-linux-gnu/libopencv_ml.so.4.1.1
uselib: /usr/lib/aarch64-linux-gnu/libopencv_objdetect.so.4.1.1
uselib: /usr/lib/aarch64-linux-gnu/libopencv_photo.so.4.1.1
uselib: /usr/lib/aarch64-linux-gnu/libopencv_stitching.so.4.1.1
uselib: /usr/lib/aarch64-linux-gnu/libopencv_video.so.4.1.1
uselib: /usr/lib/aarch64-linux-gnu/libopencv_calib3d.so.4.1.1
uselib: /usr/lib/aarch64-linux-gnu/libopencv_features2d.so.4.1.1
uselib: /usr/lib/aarch64-linux-gnu/libopencv_flann.so.4.1.1
uselib: /usr/lib/aarch64-linux-gnu/libopencv_videoio.so.4.1.1
uselib: /usr/lib/aarch64-linux-gnu/libopencv_imgcodecs.so.4.1.1
uselib: /usr/lib/aarch64-linux-gnu/libopencv_imgproc.so.4.1.1
uselib: /usr/lib/aarch64-linux-gnu/libopencv_core.so.4.1.1
uselib: /usr/lib/gcc/aarch64-linux-gnu/7/libgomp.so
uselib: /usr/lib/aarch64-linux-gnu/libpthread.so
uselib: CMakeFiles/uselib.dir/link.txt
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --green --bold --progress-dir=/home/agnext/Desktop/darknet/CMakeFiles --progress-num=$(CMAKE_PROGRESS_2) "Linking CXX executable uselib"
	$(CMAKE_COMMAND) -E cmake_link_script CMakeFiles/uselib.dir/link.txt --verbose=$(VERBOSE)

# Rule to build all files generated by this target.
CMakeFiles/uselib.dir/build: uselib

.PHONY : CMakeFiles/uselib.dir/build

CMakeFiles/uselib.dir/clean:
	$(CMAKE_COMMAND) -P CMakeFiles/uselib.dir/cmake_clean.cmake
.PHONY : CMakeFiles/uselib.dir/clean

CMakeFiles/uselib.dir/depend:
	cd /home/agnext/Desktop/darknet && $(CMAKE_COMMAND) -E cmake_depends "Unix Makefiles" /home/agnext/Desktop/darknet /home/agnext/Desktop/darknet /home/agnext/Desktop/darknet /home/agnext/Desktop/darknet /home/agnext/Desktop/darknet/CMakeFiles/uselib.dir/DependInfo.cmake --color=$(COLOR)
.PHONY : CMakeFiles/uselib.dir/depend
