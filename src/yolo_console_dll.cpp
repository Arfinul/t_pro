#include <iostream>
#include <fstream>      // Agnext, for writing file
#include <iomanip>
#include <string>
#include <vector>
#include <queue>
#include <fstream>
#include <thread>
#include <future>
#include <atomic>
#include <mutex>         // std::mutex, std::unique_lock
#include <cmath>
#include <ctime>
#include <chrono>       // Agnext TIMER
#include <sstream>      // Agnext video timestamp



// It makes sense only for video-Camera (not for video-File)
// To use - uncomment the following line. Optical-flow is supported only by OpenCV 3.x - 4.x
//define TRACK_OPTFLOW
// #define GPU

// To use 3D-stereo camera ZED - uncomment the following line. ZED_SDK should be installed.
//#define ZED_STEREO


#include "yolo_v2_class.hpp"    // imported functions from DLL

#ifdef OPENCV
#ifdef ZED_STEREO
#include <sl_zed/Camera.hpp>
#pragma comment(lib, "sl_core64.lib")
#pragma comment(lib, "sl_input64.lib")
#pragma comment(lib, "sl_zed64.lib")

float getMedian(std::vector<float> &v) {
    size_t n = v.size() / 2;
    std::nth_element(v.begin(), v.begin() + n, v.end());
    return v[n];
}

std::vector<bbox_t> get_3d_coordinates(std::vector<bbox_t> bbox_vect, cv::Mat xyzrgba)
{
    bool valid_measure;
    int i, j;
    const unsigned int R_max_global = 10;

    std::vector<bbox_t> bbox3d_vect;

    for (auto &cur_box : bbox_vect) {

        const unsigned int obj_size = std::min(cur_box.w, cur_box.h);
        const unsigned int R_max = std::min(R_max_global, obj_size / 2);
        int center_i = cur_box.x + cur_box.w * 0.5f, center_j = cur_box.y + cur_box.h * 0.5f;

        std::vector<float> x_vect, y_vect, z_vect;
        for (int R = 0; R < R_max; R++) {
            for (int y = -R; y <= R; y++) {
                for (int x = -R; x <= R; x++) {
                    i = center_i + x;
                    j = center_j + y;
                    sl::float4 out(NAN, NAN, NAN, NAN);
                    if (i >= 0 && i < xyzrgba.cols && j >= 0 && j < xyzrgba.rows) {
                        cv::Vec4f &elem = xyzrgba.at<cv::Vec4f>(j, i);  // x,y,z,w
                        out.x = elem[0];
                        out.y = elem[1];
                        out.z = elem[2];
                        out.w = elem[3];
                    }
                    valid_measure = std::isfinite(out.z);
                    if (valid_measure)
                    {
                        x_vect.push_back(out.x);
                        y_vect.push_back(out.y);
                        z_vect.push_back(out.z);
                    }
                }
            }
        }

        if (x_vect.size() * y_vect.size() * z_vect.size() > 0)
        {
            cur_box.x_3d = getMedian(x_vect);
            cur_box.y_3d = getMedian(y_vect);
            cur_box.z_3d = getMedian(z_vect);
        }
        else {
            cur_box.x_3d = NAN;
            cur_box.y_3d = NAN;
            cur_box.z_3d = NAN;
        }

        bbox3d_vect.emplace_back(cur_box);
    }

    return bbox3d_vect;
}

cv::Mat slMat2cvMat(sl::Mat &input) {
    // Mapping between MAT_TYPE and CV_TYPE
    int cv_type = -1;
    switch (input.getDataType()) {
    case sl::MAT_TYPE_32F_C1:
        cv_type = CV_32FC1;
        break;
    case sl::MAT_TYPE_32F_C2:
        cv_type = CV_32FC2;
        break;
    case sl::MAT_TYPE_32F_C3:
        cv_type = CV_32FC3;
        break;
    case sl::MAT_TYPE_32F_C4:
        cv_type = CV_32FC4;
        break;
    case sl::MAT_TYPE_8U_C1:
        cv_type = CV_8UC1;
        break;
    case sl::MAT_TYPE_8U_C2:
        cv_type = CV_8UC2;
        break;
    case sl::MAT_TYPE_8U_C3:
        cv_type = CV_8UC3;
        break;
    case sl::MAT_TYPE_8U_C4:
        cv_type = CV_8UC4;
        break;
    default:
        break;
    }
    return cv::Mat(input.getHeight(), input.getWidth(), cv_type, input.getPtr<sl::uchar1>(sl::MEM_CPU));
}

cv::Mat zed_capture_rgb(sl::Camera &zed) {
    sl::Mat left;
    zed.retrieveImage(left);
    cv::Mat left_rgb;
    cv::cvtColor(slMat2cvMat(left), left_rgb, CV_RGBA2RGB);
    return left_rgb;
}

cv::Mat zed_capture_3d(sl::Camera &zed) {
    sl::Mat cur_cloud;
    zed.retrieveMeasure(cur_cloud, sl::MEASURE_XYZ);
    return slMat2cvMat(cur_cloud).clone();
}

static sl::Camera zed; // ZED-camera

#else   // ZED_STEREO
std::vector<bbox_t> get_3d_coordinates(std::vector<bbox_t> bbox_vect, cv::Mat xyzrgba) {
    return bbox_vect;
}
#endif  // ZED_STEREO


#include <opencv2/opencv.hpp>            // C++
#include <opencv2/core/version.hpp>
#ifndef CV_VERSION_EPOCH     // OpenCV 3.x and 4.x
#include <opencv2/videoio/videoio.hpp>
#define OPENCV_VERSION CVAUX_STR(CV_VERSION_MAJOR)"" CVAUX_STR(CV_VERSION_MINOR)"" CVAUX_STR(CV_VERSION_REVISION)
#ifndef USE_CMAKE_LIBS
#pragma comment(lib, "opencv_world" OPENCV_VERSION ".lib")
#ifdef TRACK_OPTFLOW
#pragma comment(lib, "opencv_cudaoptflow" OPENCV_VERSION ".lib")
#pragma comment(lib, "opencv_cudaimgproc" OPENCV_VERSION ".lib")
#pragma comment(lib, "opencv_core" OPENCV_VERSION ".lib")
#pragma comment(lib, "opencv_imgproc" OPENCV_VERSION ".lib")
#pragma comment(lib, "opencv_highgui" OPENCV_VERSION ".lib")
#endif    // TRACK_OPTFLOW
#endif    // USE_CMAKE_LIBS
#else     // OpenCV 2.x
#define OPENCV_VERSION CVAUX_STR(CV_VERSION_EPOCH)"" CVAUX_STR(CV_VERSION_MAJOR)"" CVAUX_STR(CV_VERSION_MINOR)
#ifndef USE_CMAKE_LIBS
#pragma comment(lib, "opencv_core" OPENCV_VERSION ".lib")
#pragma comment(lib, "opencv_imgproc" OPENCV_VERSION ".lib")
#pragma comment(lib, "opencv_highgui" OPENCV_VERSION ".lib")
#pragma comment(lib, "opencv_video" OPENCV_VERSION ".lib")
#endif    // USE_CMAKE_LIBS
#endif    // CV_VERSION_EPOCH

int count_1lb = 0;  // Agnext
int count_2lb = 0; // Agnext
int count_3lb = 0;// Agnext
int count_1Banjhi = 0;// Agnext 
int count_2Banjhi = 0;// Agnext
int count_coarse = 0; // Agnext
int count_cluster = 0; // Agnext
float fine_percnt = 0.0;// Agnext
float perc_count_1lb = 0.0; //Agnext
float perc_count_2lb = 0.0; //Agnext
float perc_count_3lb = 0.0; //Agnext
float perc_count_1Banjhi = 0.0; //Agnext
float perc_count_2Banjhi = 0.0; //Agnext
float perc_count_coarse = 0.0; //Agnext
float total=0.0; //Agnext

std::string frame_str = ""; // Agnext
std::string _1lb_str = "";  // Agnext
std::string _2lb_str = "";  // Agnext
std::string _3lb_str = "";  // Agnext
std::string _1Banjhi_str = "";  // Agnext   
std::string _2Banjhi_str = "";  // Agnext
std::string coarse_str = "";    // Agnext
std::string cluster_str = "";    // Agnext
std::string _1lb_count_str = "";  // Agnext
std::string _2lb_count_str = "";  // Agnext
std::string _3lb_count_str = "";  // Agnext
std::string _1Banjhi_count_str = "";  // Agnext   
std::string _2Banjhi_count_str = "";  // Agnext
std::string _coarse_count_str = "";    // Agnext
std::string _cluster_count_str = "";    // Agnext
std::string fine_per = "";  // Agnext
std::string _timer = "";    // Agnext
std::string total_str = "";    // Agnext

// Agnext (timer)  
double duration;    // Agnext
int seconds, minutes, hours; // Agnext

int tap_count = 0;
int image_width = 0;
int image_height = 0;
bool double_tap = false;
bool countdown_started = false;
auto start_tap_sec_count = std::chrono::high_resolution_clock::now();
auto end_tap_sec_count = std::chrono::high_resolution_clock::now();
auto start_no_frame_sec_count = std::chrono::high_resolution_clock::now();
auto end_no_frame_sec_count = std::chrono::high_resolution_clock::now();

cv::Mat black_image(480, 640, CV_8UC3); // Agnext black image
bool black_background = false;
bool clean_video = true;
int sec_for_empty_frame = 45;
int double_tap_seconds_close = 5;   

void draw_boxes(cv::Mat mat_img, std::vector<bbox_t> result_vec, std::vector<std::string> obj_names,
    int current_det_fps = -1, int current_cap_fps = -1, bool black_screen=false)
{
    // // UNCOMMENTED FOR DEVELOPER MODE
    // int const colors[6][3] = { { 1,0,1 },{ 0,0,1 },{ 0,1,1 },{ 0,1,0 },{ 1,1,0 },{ 1,0,0 } };       // Agnext
    // if (black_screen == false)
    // {
    //     for (auto &i : result_vec) {
    //         cv::Scalar color = obj_id_to_color(i.obj_id);
    //         // cv::rectangle(mat_img, cv::Rect(i.x, i.y, i.w, i.h), color, 2);
    //         // if (obj_names.size() > i.obj_id) {
    //         if (obj_names.size() > i.obj_id && result_vec.size() > 0) {
    //             std::string obj_name = obj_names[i.obj_id];
    //             if (i.track_id > 0) obj_name += " - " + std::to_string(i.track_id);
    //             cv::Size const text_size = getTextSize(obj_name, cv::FONT_HERSHEY_COMPLEX_SMALL, 1.2, 2, 0);
    //             int max_width = (text_size.width > i.w + 2) ? text_size.width : (i.w + 2);
    //             max_width = std::max(max_width, (int)i.w + 2);
    //             //max_width = std::max(max_width, 283);
    //             std::string coords_3d;
    //             if (!std::isnan(i.z_3d)) {
    //                 std::stringstream ss;
    //                 // ss << std::fixed << std::setprecision(2) << "x:" << i.x_3d << "m y:" << i.y_3d << "m z:" << i.z_3d << "m ";  // Agnext, originall uncommented
    //                 coords_3d = ss.str();
    //                 cv::Size const text_size_3d = getTextSize(ss.str(), cv::FONT_HERSHEY_COMPLEX_SMALL, 0.8, 1, 0);
    //                 int const max_width_3d = (text_size_3d.width > i.w + 2) ? text_size_3d.width : (i.w + 2);
    //                 if (max_width_3d > max_width) max_width = max_width_3d;
    //             }
    //             std::string folder_name = "";
    //             if (obj_names[i.obj_id] == "1Banjhi"){
    //                 folder_name = "1bj/";
    //             }
    //             else if (obj_names[i.obj_id] == "2Banjhi"){
    //                 folder_name = "2bj/";
    //             }
    //             else if (obj_names[i.obj_id] == "1LB"){
    //                 folder_name = "1lb/";
    //             }
    //             else if (obj_names[i.obj_id] == "2LB"){
    //                 folder_name = "2lb/";
    //             }
    //             else if (obj_names[i.obj_id] == "3LB"){
    //                 folder_name = "3lb/";
    //             }
    //             else if (obj_names[i.obj_id] == "Coarse"){
    //                 folder_name = "coarse/";
    //             }
    //             else if (obj_names[i.obj_id] == "Cluster"){
    //                 folder_name = "cluster/";
    //             }
    //             std::string img_name = "reports/" + folder_name + obj_name + ".png";
    //             std::ifstream infile(img_name);
    //             if (infile.good()){}
    //             else{
    //                 cv::Mat crop = mat_img(cv::Rect(i.x, i.y, i.w, i.h));
    //                 cv::imwrite(img_name, crop);
    //             }

    //             // cv::rectangle(mat_img, cv::Point2f(std::max((int)i.x - 1, 0), std::max((int)i.y - 35, 0)),
    //             //     cv::Point2f(std::min((int)i.x + max_width, mat_img.cols - 1), std::min((int)i.y, mat_img.rows - 1)),
    //             //     color, CV_FILLED, 8, 0);
    //             // putText(mat_img, obj_name, cv::Point2f(i.x, i.y - 16), cv::FONT_HERSHEY_COMPLEX_SMALL, 1.2, cv::Scalar(0, 0, 0), 2); // original

    //             // std::string frame_str = "FRAME: " + std::to_string(frame_id);
    //             // putText(mat_img, frame_str, cv::Point2f(10, 50), cv::FONT_HERSHEY_COMPLEX_SMALL, 1.2, cv::Scalar(0, 255, 255), 1);  // Agnext

    //             // putText(mat_img, obj_name, cv::Point2f(i.x, i.y - 16), cv::FONT_HERSHEY_COMPLEX_SMALL, 1, cv::Scalar(0, 0, 0), 2); // Agnext
    //             if(!coords_3d.empty()) putText(mat_img, coords_3d, cv::Point2f(i.x, i.y-1), cv::FONT_HERSHEY_COMPLEX_SMALL, 0.8, cv::Scalar(0, 0, 0), 1);
    //         }
    //     }
    // } OR BELOW CODE

   // // UNCOMMENTED FOR DEVELOPER MODE
    //int const colors[6][3] = { { 1,0,1 },{ 0,0,1 },{ 0,1,1 },{ 0,1,0 },{ 1,1,0 },{ 1,0,0 } };       // Agnext
   // if (black_screen == false)
   // {
    //    for (auto &i : result_vec) {
    //        cv::Scalar color = obj_id_to_color(i.obj_id);
    //        cv::rectangle(mat_img, cv::Rect(i.x, i.y, i.w, i.h), color, 2);
     //       // if (obj_names.size() > i.obj_id) {
    //        if (obj_names.size() > i.obj_id && result_vec.size() > 0) {
     //           std::string obj_name = obj_names[i.obj_id];
     //           if (i.track_id > 0) obj_name += " - " + std::to_string(i.track_id);
     //           cv::Size const text_size = getTextSize(obj_name, cv::FONT_HERSHEY_COMPLEX_SMALL, 1.2, 2, 0);
      //          int max_width = (text_size.width > i.w + 2) ? text_size.width : (i.w + 2);
       //         max_width = std::max(max_width, (int)i.w + 2);
      //          //max_width = std::max(max_width, 283);
        //        std::string coords_3d;
        //        if (!std::isnan(i.z_3d)) {
        //            std::stringstream ss;
         //           // ss << std::fixed << std::setprecision(2) << "x:" << i.x_3d << "m y:" << i.y_3d << "m z:" << i.z_3d << "m ";  // Agnext, originall uncommented
          //          coords_3d = ss.str();
          //          cv::Size const text_size_3d = getTextSize(ss.str(), cv::FONT_HERSHEY_COMPLEX_SMALL, 0.8, 1, 0);
           //         int const max_width_3d = (text_size_3d.width > i.w + 2) ? text_size_3d.width : (i.w + 2);
          //          if (max_width_3d > max_width) max_width = max_width_3d;
          //      }

          //      cv::rectangle(mat_img, cv::Point2f(std::max((int)i.x - 1, 0), std::max((int)i.y - 35, 0)),
          //          cv::Point2f(std::min((int)i.x + max_width, mat_img.cols - 1), std::min((int)i.y, mat_img.rows - 1)),
          //          color, CV_FILLED, 8, 0);
          //      // putText(mat_img, obj_name, cv::Point2f(i.x, i.y - 16), cv::FONT_HERSHEY_COMPLEX_SMALL, 1.2, cv::Scalar(0, 0, 0), 2); // original

           //     // std::string frame_str = "FRAME: " + std::to_string(frame_id);
           //     // putText(mat_img, frame_str, cv::Point2f(10, 50), cv::FONT_HERSHEY_COMPLEX_SMALL, 1.2, cv::Scalar(0, 255, 255), 1);  // Agnext

           //     putText(mat_img, obj_name, cv::Point2f(i.x, i.y - 16), cv::FONT_HERSHEY_COMPLEX_SMALL, 1, cv::Scalar(0, 0, 0), 2); // Agnext
            //    if(!coords_3d.empty()) putText(mat_img, coords_3d, cv::Point2f(i.x, i.y-1), cv::FONT_HERSHEY_COMPLEX_SMALL, 0.8, cv::Scalar(0, 0, 0), 1);
          //  }
      //  }
    //}

    if (current_det_fps >= 0 && current_cap_fps >= 0) {

        std::string fps_str = "FPS detection: " + std::to_string(current_det_fps) + "   FPS capture: " + std::to_string(current_cap_fps);
        putText(mat_img, fps_str, cv::Point2f(10, 20), cv::FONT_HERSHEY_COMPLEX_SMALL, 1.2, cv::Scalar(50, 255, 0), 2);
    }
}
#endif    // OPENCV


void show_console_result(std::vector<bbox_t> const result_vec, std::vector<std::string> const obj_names, int frame_id = -1) {
    for (auto &i : result_vec) {
        if (i.obj_id == 6){
            if (frame_id >= 0 && result_vec.size() > 0) std::cout << "Frame: " << frame_id << std::endl;
            if (obj_names.size() > i.obj_id) std::cout << obj_names[i.obj_id] << " - ";
            std::cout << "track_id = " << i.track_id << ", obj_id = " << i.obj_id << ", x = " << i.x << ", y = " << i.y
                << ", w = " << i.w/float(image_width) << ", h = " << i.h/float(image_height)
                << std::setprecision(3) << ", prob = " << i.prob << std::endl;
        }
    }
}

void writeFile(std::string frame_str, std::string _1lb_str, std::string _2lb_str, std::string _3lb_str, std::string _1Banjhi_str, std::string _2Banjhi_str, std::string coarse_str, std::string cluster_str, std::string fine_per, std::string _timer) 
{
  std::ofstream myfile;
  myfile.open("result.txt");    // Agnext changes file name
  myfile <<frame_str<<"\n";
  myfile <<_1lb_str<<"\n";
  myfile <<_2lb_str<<"\n";
  myfile <<_3lb_str<<"\n";
  myfile <<_1Banjhi_str<<"\n";  
  myfile <<_2Banjhi_str<<"\n";
  myfile <<cluster_str<<"\n";
  myfile <<coarse_str<<"\n";
  myfile <<fine_per<<"\n";
  myfile <<_timer<<"\n";
  myfile.close();
}

// close on touch // AgNext
struct detection_data_t {
                    cv::Mat cap_frame;
                    std::shared_ptr<image_t> det_image;
                    std::vector<bbox_t> result_vec;
                    cv::Mat draw_frame;
                    cv::Mat save_video_frame;
                    bool new_detection;
                    uint64_t frame_id;
                    bool exit_flag;
                    cv::Mat zed_cloud;
                    std::queue<cv::Mat> track_optflow_queue;
                    detection_data_t() : exit_flag(false), new_detection(false) {}
                };


static void onMouse( int event, int x, int y, int, void* param)
{
    if (tap_count > 1){
        double_tap = true; 
    }
    else{
        tap_count ++;
    }
}

// close on touch // AgNext


std::vector<std::string> objects_names_from_file(std::string const filename) {
    std::ifstream file(filename);
    std::vector<std::string> file_lines;
    if (!file.is_open()) return file_lines;
    for(std::string line; getline(file, line);) file_lines.push_back(line);
    // std::cout << "object names loaded \n";  // AgNext, originally uncommented
    return file_lines;
}

template<typename T>
class send_one_replaceable_object_t {
    const bool sync;
    std::atomic<T *> a_ptr;
public:

    void send(T const& _obj) {
        T *new_ptr = new T;
        *new_ptr = _obj;
        if (sync) {
            while (a_ptr.load()) std::this_thread::sleep_for(std::chrono::milliseconds(3));
        }
        std::unique_ptr<T> old_ptr(a_ptr.exchange(new_ptr));
    }

    T receive() {
        std::unique_ptr<T> ptr;
        do {
            while(!a_ptr.load()) std::this_thread::sleep_for(std::chrono::milliseconds(3));
            ptr.reset(a_ptr.exchange(NULL));
        } while (!ptr);
        T obj = *ptr;
        return obj;
    }

    bool is_object_present() {
        return (a_ptr.load() != NULL);
    }

    send_one_replaceable_object_t(bool _sync) : sync(_sync), a_ptr(NULL)
    {}
};

int main(int argc, char *argv[])
{
    std::string  names_file = "data/coco.names";
    std::string  cfg_file = "cfg/yolov3.cfg";
    std::string  weights_file = "yolov3.weights";
    std::string filename;
    
    int capture_width = 640 ;
    int capture_height = 480 ;
    int display_width = 640 ;
    int display_height = 480 ;
    int framerate = 30 ;
    int flip_method = 0 ;

    std::string gst_pipeline = "nvarguscamerasrc ! video/x-raw(memory:NVMM), width=(int)" + std::to_string(capture_width) + ", height=(int)" + std::to_string(capture_height) + ", format=(string)NV12, framerate=(fraction)" + std::to_string(framerate) + "/1 ! nvvidconv flip-method=" + std::to_string(flip_method) + " ! video/x-raw, width=(int)" + std::to_string(display_width) + ", height=(int)" + std::to_string(display_height) + ", format=(string)BGRx ! videoconvert ! video/x-raw, format=(string)BGR ! appsink";

    auto t_start = std::chrono::high_resolution_clock::now(); // Agnext TIMER

    if (argc > 4) {    //voc.names yolo-voc.cfg yolo-voc.weights test.mp4
        names_file = argv[1];
        cfg_file = argv[2];
        weights_file = argv[3];
        filename = argv[4];
    }
    else if (argc > 1) filename = argv[1];

    float const thresh = (argc > 5) ? std::stof(argv[5]) : 0.63;

    Detector detector(cfg_file, weights_file);

    auto obj_names = objects_names_from_file(names_file);
    
    // timestamp for videoname
    auto t = std::time(nullptr);
    auto tm = *std::localtime(&t);
    std::ostringstream oss;
    oss << std::put_time(&tm, "%d-%m-%Y %H-%M-%S");
    auto str = oss.str();

    std::string out_videofile = "flc_utils/trainVideo/testing/result.avi";
    bool const save_output_videofile = true;   // true - for history
    bool const send_network = false;        // true - for remote detection
    bool const use_kalman_filter = true;   // true - for stationary camera

    bool detection_sync = false;             // true - for video-file
    //bool detection_sync = false;   //Agnext commented, for detection on each frame, this solve blinking issue
#ifdef TRACK_OPTFLOW    // for slow GPU
    detection_sync = false;   //Agnext commented, for detection on each frame, this solve blinking issue
    Tracker_optflow tracker_flow;
    //detector.wait_stream = true;
#endif  // TRACK_OPTFLOW


    while (true)
    {
        //std::cout << "input image or video filename: ";  //AgNext, original uncommented
        if(filename.size() == 0) std::cin >> filename;
        if (filename.size() == 0) break;

        try {
#ifdef OPENCV
            preview_boxes_t large_preview(100, 150, false), small_preview(50, 50, true);
            bool show_small_boxes = false;

            std::string const file_ext = filename.substr(filename.find_last_of(".") + 1);
            std::string const protocol = filename.substr(0, 7);
            if (file_ext == "MTS" || file_ext == "avi" || file_ext == "mp4" || file_ext == "mjpg" || file_ext == "mov" ||     // video file
                protocol == "rtmp://" || protocol == "rtsp://" || protocol == "http://" || protocol == "https:/" ||    // video network stream
                filename == "zed_camera" || file_ext == "svo" || filename == "web_camera")   // ZED stereo camera

            {
                if (protocol == "rtsp://" || protocol == "http://" || protocol == "https:/" || filename == "zed_camera" || filename == "web_camera")
                    detection_sync = false;

                cv::Mat cur_frame;
                std::atomic<int> fps_cap_counter(0), fps_det_counter(0);
                std::atomic<int> current_fps_cap(0), current_fps_det(0);
                std::atomic<bool> exit_flag(false);
                std::chrono::steady_clock::time_point steady_start, steady_end;
                int video_fps = 25;
                bool use_zed_camera = false;

                track_kalman_t track_kalman;

#ifdef ZED_STEREO
                sl::InitParameters init_params;
                init_params.depth_minimum_distance = 0.5;
                init_params.depth_mode = sl::DEPTH_MODE_ULTRA;
                init_params.camera_resolution = sl::RESOLUTION_HD720;// sl::RESOLUTION_HD1080, sl::RESOLUTION_HD720
                init_params.coordinate_units = sl::UNIT_METER;
                //init_params.sdk_cuda_ctx = (CUcontext)detector.get_cuda_context();
                init_params.sdk_gpu_id = detector.cur_gpu_id;
                init_params.camera_buffer_count_linux = 2;
                if (file_ext == "svo") init_params.svo_input_filename.set(filename.c_str());
                if (filename == "zed_camera" || file_ext == "svo") {
                    std::cout << "ZED 3D Camera " << zed.open(init_params) << std::endl;
                    if (!zed.isOpened()) {
                        std::cout << " Error: ZED Camera should be connected to USB 3.0. And ZED_SDK should be installed. \n";
                        getchar();
                        return 0;
                    }
                    cur_frame = zed_capture_rgb(zed);
                    use_zed_camera = true;
                }
#endif  // ZED_STEREO

                cv::VideoCapture cap(gst_pipeline);
                if (filename == "web_camera") {
                    if(!cap.isOpened()) {
			std::cout<<"Failed to open camera."<<std::endl;
			return (-1);
		    }
                    cap >> cur_frame;
                } else if (!use_zed_camera) {
                    cap.open(filename);
                    cap >> cur_frame;
                }
#ifdef CV_VERSION_EPOCH // OpenCV 2.x
                video_fps = cap.get(CV_CAP_PROP_FPS);
#else
                video_fps = cap.get(cv::CAP_PROP_FPS);
#endif
                cv::Size const frame_size = cur_frame.size(); // Original
                image_width = frame_size.width;
                image_height = frame_size.height;
                // cv::Size const frame_size(cap.get(CV_CAP_PROP_FRAME_WIDTH), cap.get(CV_CAP_PROP_FRAME_HEIGHT));
                // cv::Size const frame_size(1280, 720);    // Agnext FRAME RESIZE
                // cv::Size const frame_size(1920, 1080); // Agnext FRAME RESIZE
        // cv::Size const frame_size(512, 384); // Agnext FRAME RESIZE
                // std::cout << "\n Video size: " << frame_size << std::endl;  // AgNext, originally uncommented

                cv::VideoWriter output_video;
                if (save_output_videofile)
#ifdef CV_VERSION_EPOCH // OpenCV 2.x
                    // output_video.open(out_videofile, CV_FOURCC('D', 'I', 'V', 'X'), std::max(35, video_fps), frame_size, true);  // Original
                    output_video.open(out_videofile, CV_FOURCC('D', 'I', 'V', 'X'), std::max(1, video_fps), frame_size, true);  // Agnext
#else
                    // output_video.open(out_videofile, cv::VideoWriter::fourcc('D', 'I', 'V', 'X'), std::max(35, video_fps), frame_size, true);
                output_video.open(out_videofile, cv::VideoWriter::fourcc('D', 'I', 'V', 'X'), std::max(1, video_fps), frame_size, true);  // AgNext
#endif

                const bool sync = detection_sync; // sync data exchange
                send_one_replaceable_object_t<detection_data_t> cap2prepare(sync), cap2draw(sync),
                    prepare2detect(sync), detect2draw(sync), draw2show(sync), draw2write(sync), draw2net(sync);

                std::thread t_cap, t_prepare, t_detect, t_post, t_draw, t_write, t_network;

                // capture new video-frame
                if (t_cap.joinable()) t_cap.join();
                t_cap = std::thread([&]()
                {
                    uint64_t frame_id = 0;
                    detection_data_t detection_data;
                    do {
                        detection_data = detection_data_t();
#ifdef ZED_STEREO
                        if (use_zed_camera) {
                            while (zed.grab() != sl::SUCCESS) std::this_thread::sleep_for(std::chrono::milliseconds(2));
                            detection_data.cap_frame = zed_capture_rgb(zed);
                            detection_data.zed_cloud = zed_capture_3d(zed);
                        }
                        else
#endif   // ZED_STEREO
                        {
                            cap >> detection_data.cap_frame;
                        }
                        fps_cap_counter++;
                        detection_data.frame_id = frame_id++;
                        if (detection_data.cap_frame.empty() || exit_flag) {
                            //std::cout << " exit_flag: detection_data.cap_frame.size = " << detection_data.cap_frame.size() << std::endl;  //AgNext, originall was uncomented
                            detection_data.exit_flag = true;
                            detection_data.cap_frame = cv::Mat(frame_size, CV_8UC3);
                        }

                        if (!detection_sync) {
                            cap2draw.send(detection_data);       // skip detection
                        }
                        cap2prepare.send(detection_data);
                    } while (!detection_data.exit_flag);
                    // std::cout << " t_cap exit \n";  //AgNext, originall was uncomented
                });


                // pre-processing video frame (resize, convertion)
                t_prepare = std::thread([&]()
                {
                    std::shared_ptr<image_t> det_image;
                    detection_data_t detection_data;
                    do {
                        detection_data = cap2prepare.receive();

                        det_image = detector.mat_to_image_resize(detection_data.cap_frame);
                        detection_data.det_image = det_image;
                        prepare2detect.send(detection_data);    // detection

                    } while (!detection_data.exit_flag);
                    // std::cout << " t_prepare exit \n";  //AgNext, originall was uncomented
                });


                // detection by Yolo
                if (t_detect.joinable()) t_detect.join();
                t_detect = std::thread([&]()
                {
                    std::shared_ptr<image_t> det_image;
                    detection_data_t detection_data;
                    do {
                        detection_data = prepare2detect.receive();
                        det_image = detection_data.det_image;
                        std::vector<bbox_t> result_vec;

                        if(det_image)
                            result_vec = detector.detect_resized(*det_image, frame_size.width, frame_size.height, thresh, true);  // true
                        fps_det_counter++;
                        //std::this_thread::sleep_for(std::chrono::milliseconds(150));

                        detection_data.new_detection = true;
                        detection_data.result_vec = result_vec;
                        detect2draw.send(detection_data);
                    } while (!detection_data.exit_flag);
                    // std::cout << " t_detect exit \n";  //AgNext, originall was uncomented
                });

                // draw rectangles (and track objects)
                t_draw = std::thread([&]()
                {
                    std::queue<cv::Mat> track_optflow_queue;
                    detection_data_t detection_data;
                    do {

                        // for Video-file
                        if (detection_sync) {
                            detection_data = detect2draw.receive();
                        }
                        // for Video-camera
                        else
                        {
                            // get new Detection result if present
                            if (detect2draw.is_object_present()) {
                                cv::Mat old_cap_frame = detection_data.cap_frame;   // use old captured frame
                                detection_data = detect2draw.receive();
                                if (!old_cap_frame.empty()) detection_data.cap_frame = old_cap_frame;
                            }
                            // get new Captured frame
                            else {
                                std::vector<bbox_t> old_result_vec = detection_data.result_vec; // use old detections
                                detection_data = cap2draw.receive();
                                detection_data.result_vec = old_result_vec;
                            }
                        }

                        cv::Mat cap_frame = detection_data.cap_frame;
                        cv::Mat draw_frame = detection_data.cap_frame.clone();
                        std::vector<bbox_t> result_vec = detection_data.result_vec;

#ifdef TRACK_OPTFLOW
                        if (detection_data.new_detection) {
                            tracker_flow.update_tracking_flow(detection_data.cap_frame, detection_data.result_vec);
                            while (track_optflow_queue.size() > 0) {
                                draw_frame = track_optflow_queue.back();
                                result_vec = tracker_flow.tracking_flow(track_optflow_queue.front(), false);
                                track_optflow_queue.pop();
                            }
                        }
                        else {
                            track_optflow_queue.push(cap_frame);
                            // result_vec = tracker_flow.tracking_flow(cap_frame, false); // Original
                            result_vec = tracker_flow.tracking_flow(cap_frame, true);  // Agnext, to remove moving boxes when objects disappear
                        }
                        detection_data.new_detection = true;    // to correct kalman filter
#endif //TRACK_OPTFLOW

                        // track ID by using kalman filter
                        if (use_kalman_filter) {
                            if (detection_data.new_detection) {
                                result_vec = track_kalman.correct(result_vec);
                            }
                            else {
                                result_vec = track_kalman.predict();
                            }
                        }
                        // track ID by using custom function
                        else {
                            int frame_story = std::max(5, current_fps_cap.load());
                            result_vec = detector.tracking_id(result_vec, true, frame_story, 40);
                        }

                        if (use_zed_camera && !detection_data.zed_cloud.empty()) {
                            result_vec = get_3d_coordinates(result_vec, detection_data.zed_cloud);
                        }

                        cv::Mat copy_draw_frame = draw_frame.clone();
                        //small_preview.set(draw_frame, result_vec);
                        //large_preview.set(draw_frame, result_vec);
                        if (black_background){
                            resize(draw_frame, draw_frame, cv::Size(640, 480), 0, 0, CV_INTER_CUBIC);   // Agnext FRAME RESIZE
                            black_image.copyTo(draw_frame(cv::Rect(0,0, black_image.cols, black_image.rows)));      // Agnext (put black image as bg) // COMMENTED FOR DEVELOPER MODE

                        }
                        // resize(draw_frame, draw_frame, cv::Size(680, 480), 0, 0, CV_INTER_CUBIC);  // Agnext FRAME RESIZE
                        draw_boxes(draw_frame, result_vec, obj_names, current_fps_det, current_fps_cap, black_background);
                        show_console_result(result_vec, obj_names, detection_data.frame_id); // Agnext, originall was commented // UNCOMMENTED FOR DEVELOPER MODE
                        
                        for (auto &i : result_vec) {        // Agnext, added for counting fine counts
                            if (obj_names.size() > i.obj_id) 
                                if (obj_names[i.obj_id] == "1LB"){
                                    count_1lb = i.track_id;
                                    start_no_frame_sec_count = std::chrono::high_resolution_clock::now();
                                }
                                else if (obj_names[i.obj_id] == "2LB"){
                                    count_2lb = i.track_id;
                                    start_no_frame_sec_count = std::chrono::high_resolution_clock::now();
                                }
                                else if (obj_names[i.obj_id] == "3LB"){
                                    count_3lb = i.track_id;
                                    start_no_frame_sec_count = std::chrono::high_resolution_clock::now();
                                }
                                else if (obj_names[i.obj_id] == "1Banjhi"){ 
                                    count_1Banjhi = i.track_id; 
                                    start_no_frame_sec_count = std::chrono::high_resolution_clock::now();
                                }   
                                else if (obj_names[i.obj_id] == "2Banjhi"){ 
                                    count_2Banjhi = i.track_id; 
                                    start_no_frame_sec_count = std::chrono::high_resolution_clock::now();
                                }
                                else if (obj_names[i.obj_id] == "Coarse"){
                                    count_coarse = i.track_id;
                                    start_no_frame_sec_count = std::chrono::high_resolution_clock::now();
                                }
                                else if (obj_names[i.obj_id] == "Cluster"){
                                    count_cluster = i.track_id;
                                    start_no_frame_sec_count = std::chrono::high_resolution_clock::now();
                                }
                        }
                        
                        total = (count_1lb + count_2lb + count_3lb + count_1Banjhi + count_2Banjhi + count_coarse);

                        if (double_tap == true){
                            putText(draw_frame, "Exiting...", cv::Point2f(250, 360), cv::FONT_HERSHEY_COMPLEX_SMALL, 1.2, cv::Scalar(0, 0, 255), 2); // Agnext
                        }
                        else{
                            putText(draw_frame, "Double Tap to Exit", cv::Point2f(200, 360), cv::FONT_HERSHEY_COMPLEX_SMALL, 1.2, cv::Scalar(0, 0, 255), 2); // Agnext
                        }

                        frame_str = "FRAME : " + std::to_string(detection_data.frame_id); // Agnext
                        // putText(draw_frame, frame_str, cv::Point2f(10, 50), cv::FONT_HERSHEY_COMPLEX_SMALL, 1.2, cv::Scalar(50, 255, 0), 2); // Agnext

                        perc_count_1lb = (float(count_1lb)*100)/total;
                        _1lb_count_str = "1LB : " + std::to_string(count_1lb); // Agnext
                        _1lb_str = "1LB %: " + std::to_string(perc_count_1lb); // Agnext
                        // putText(draw_frame, _1lb_str.substr(0,11), cv::Point2f(10, 100), cv::FONT_HERSHEY_COMPLEX_SMALL, 1.2, cv::Scalar(0, 255, 255), 1);  // Agnext

                        perc_count_2lb = (float(count_2lb)*100)/total;
                        _2lb_count_str = "2LB : " + std::to_string(count_2lb); // Agnext
                        _2lb_str = "2LB %: " + std::to_string(perc_count_2lb); // Agnext
                        // putText(draw_frame, _2lb_str.substr(0,11), cv::Point2f(10, 130), cv::FONT_HERSHEY_COMPLEX_SMALL, 1.2, cv::Scalar(0, 255, 255), 1);  // Agnext

                        perc_count_3lb = ((float(count_3lb/2)*100)/total);
                        _3lb_count_str = "3LB : " + std::to_string(count_3lb); // Agnext
                        _3lb_str = "3LB %: " + std::to_string(perc_count_3lb); // Agnext
                        // putText(draw_frame, _3lb_str.substr(0,11), cv::Point2f(10, 160), cv::FONT_HERSHEY_COMPLEX_SMALL, 1.2, cv::Scalar(0, 255, 255), 1);  // Agnext

                        perc_count_1Banjhi = (float(count_1Banjhi)*100)/total;
                        _1Banjhi_count_str = "1Banjhi : " + std::to_string(count_1Banjhi); // Agnext
                        _1Banjhi_str = "1Banjhi %: " + std::to_string(perc_count_1Banjhi); // Agnext    
                        // putText(draw_frame, _1Banjhi_str.substr(0,15), cv::Point2f(10, 190), cv::FONT_HERSHEY_COMPLEX_SMALL, 1.2, cv::Scalar(0, 255, 255), 1);  // Agnext   
                        
                        perc_count_2Banjhi = (float(count_2Banjhi)*100)/total;
                        _2Banjhi_count_str = "2Banjhi : " + std::to_string(count_2Banjhi); // Agnext
                        _2Banjhi_str = "2Banjhi %: " + std::to_string(perc_count_2Banjhi); // Agnext    
                        // putText(draw_frame, _2Banjhi_str.substr(0,15), cv::Point2f(10, 220), cv::FONT_HERSHEY_COMPLEX_SMALL, 1.2, cv::Scalar(0, 255, 255), 1);  // Agnext

                        _cluster_count_str = "Cluster : " + std::to_string(count_cluster); // Agnext

                        perc_count_coarse = (float(count_coarse)*100)/total;
                        _coarse_count_str = "Coarse : " + std::to_string(count_coarse); // Agnext
                        coarse_str = "Coarse %: " + std::to_string(perc_count_coarse); // Agnext
                        putText(draw_frame, coarse_str.substr(0,14), cv::Point2f(10, 100), cv::FONT_HERSHEY_COMPLEX_SMALL, 1.2, cv::Scalar(0, 255, 255), 2);  // Agnext

                        fine_percnt = (float(count_1lb) + float(count_2lb) + float(count_1Banjhi)) * 100 / total; // Agnext

                        fine_per = "FLC % : " + std::to_string(fine_percnt); // Agnext
                        putText(draw_frame, fine_per.substr(0,12), cv::Point2f(10, 50), cv::FONT_HERSHEY_COMPLEX_SMALL, 1.2, cv::Scalar(0, 255, 255), 2);  // Agnext

                        total_str = "Total : " + std::to_string(total); // Agnext
                        // putText(draw_frame, total_str, cv::Point2f(10, 310), cv::FONT_HERSHEY_COMPLEX_SMALL, 1.2, cv::Scalar(0, 255, 255), 1);  // Agnext
                        
                        // TIMER
                        auto t_end = std::chrono::high_resolution_clock::now(); // Agnext
                        duration = std::chrono::duration<double, std::milli>(t_end-t_start).count(); // Agnext

                        seconds = int(duration/1000);// Agnext
                        minutes = seconds / 60; // Agnext
                        hours = minutes / 60;// Agnext

                        _timer = "TIMER : " + std::to_string(int(hours)) + "H " + std::to_string(int(minutes%60)) + "M " + std::to_string(seconds%60) + "S"; // Agnext
                        putText(draw_frame, _timer, cv::Point2f(10, 340), cv::FONT_HERSHEY_COMPLEX_SMALL, 1.2, cv::Scalar(0, 255, 255), 1);  // Agnext

                        //large_preview.draw(draw_frame);
                        //small_preview.draw(draw_frame, true);

                        detection_data.result_vec = result_vec;
                        detection_data.draw_frame = draw_frame;
                        if (clean_video){
                            detection_data.save_video_frame = copy_draw_frame;
                        }
                        else{
                            detection_data.save_video_frame = draw_frame;
                        }
                        
                        draw2show.send(detection_data);
                        if (send_network) draw2net.send(detection_data);
                        if (output_video.isOpened()) draw2write.send(detection_data);
                    } while (!detection_data.exit_flag);
                    // std::cout << " t_draw exit \n";  //AgNext, originall was uncomented
                });


                // write frame to videofile
                t_write = std::thread([&]()
                {
                    if (output_video.isOpened()) {
                        detection_data_t detection_data;
                        cv::Mat output_frame;
                        do {
                            detection_data = draw2write.receive();
                            if(detection_data.save_video_frame.channels() == 4) cv::cvtColor(detection_data.save_video_frame, output_frame, CV_RGBA2RGB);
                            else output_frame = detection_data.save_video_frame;
                            // resize(output_frame, output_frame, cv::Size(1280, 720), 0, 0, CV_INTER_CUBIC);   // Agnext FRAME RESIZE
                            // resize(output_frame, output_frame, cv::Size(1920, 1080), 0, 0, CV_INTER_CUBIC);  // Agnext FRAME RESIZE
                            output_video << output_frame;
                        } while (!detection_data.exit_flag);
                        output_video.release();
                    }
                    // std::cout << " t_write exit \n";  //AgNext, originall was uncomented
                });

                // send detection to the network
                t_network = std::thread([&]()
                {
                    if (send_network) {
                        detection_data_t detection_data;
                        do {
                            detection_data = draw2net.receive();

                            detector.send_json_http(detection_data.result_vec, obj_names, detection_data.frame_id, filename);

                        } while (!detection_data.exit_flag);
                    }
                    // std::cout << " t_network exit \n";  //AgNext, originall was uncomented
                });


                // show detection
                detection_data_t detection_data;
                do {

                    steady_end = std::chrono::steady_clock::now();
                    float time_sec = std::chrono::duration<double>(steady_end - steady_start).count();
                    if (time_sec >= 1) {
                        current_fps_det = fps_det_counter.load() / time_sec;
                        current_fps_cap = fps_cap_counter.load() / time_sec;
                        steady_start = steady_end;
                        fps_det_counter = 0;
                        fps_cap_counter = 0;
                    }

                    detection_data = draw2show.receive();
                    cv::Mat draw_frame = detection_data.draw_frame;

                    //if (extrapolate_flag) {
                    //    cv::putText(draw_frame, "extrapolate", cv::Point2f(10, 40), cv::FONT_HERSHEY_COMPLEX_SMALL, 1.0, cv::Scalar(50, 50, 0), 2);
                    //}
                    // resize(draw_frame, draw_frame, cv::Size(1280, 720), 0, 0, CV_INTER_CUBIC);   // Agnext FRAME RESIZE
                    // resize(draw_frame, draw_frame, cv::Size(1920, 1080), 0, 0, CV_INTER_CUBIC); 
                    cv::imshow("window", draw_frame);
                    cv::moveWindow("window", 70, 100);     // Agnext (move window for tkinter interface)
                	
                    // AUTO-CLOSE AFTER 30 SEC ON EMPTY FRAME
                    end_no_frame_sec_count = std::chrono::high_resolution_clock::now();
                	if (int(std::chrono::duration<double, std::milli>(end_no_frame_sec_count-start_no_frame_sec_count).count() / 1000) > (sec_for_empty_frame*1)){
                		writeFile(frame_str, _1lb_count_str, _2lb_count_str, _3lb_count_str, _1Banjhi_count_str, _2Banjhi_count_str, _coarse_count_str, _cluster_count_str, fine_per.substr(0,12), _timer); // Agnext write to file
                    	exit_flag = true;
                	}

                	// CLOSE AFTER "double_tap_seconds_close" SEC OF DOUBLE TAP
                	if (double_tap == true){
                		end_tap_sec_count = std::chrono::high_resolution_clock::now();

                		if (countdown_started == false){
                			countdown_started = true;
                			start_tap_sec_count = std::chrono::high_resolution_clock::now();
                		}

                		if ((int(std::chrono::duration<double, std::milli>(end_tap_sec_count-start_tap_sec_count).count() / 1000) > (double_tap_seconds_close * 1)) && (countdown_started == true)){
                			writeFile(frame_str, _1lb_count_str, _2lb_count_str, _3lb_count_str, _1Banjhi_count_str, _2Banjhi_count_str, _coarse_count_str, _cluster_count_str, fine_per.substr(0,12), _timer); // Agnext write to file
				        	exit_flag = true;
                		}
                	}
                    
                    int key = cv::waitKey(3);    // 3 or 16ms
                    if (key == 'f') show_small_boxes = !show_small_boxes;
                    if (key == 'p') while (true) if (cv::waitKey(100) == 'p') break;
                    //if (key == 'e') extrapolate_flag = !extrapolate_flag;
                    if (key == 27 || key == 'q'|| cv::getWindowProperty("window", cv::WND_PROP_ASPECT_RATIO) < 0) { 
                        writeFile(frame_str, _1lb_count_str, _2lb_count_str, _3lb_count_str, _1Banjhi_count_str, _2Banjhi_count_str, _coarse_count_str, _cluster_count_str, fine_per.substr(0,12), _timer); // Agnext write to file
                        exit_flag = true;}   // Agnext (Exit on p key as well)
                    cv::setMouseCallback("window", onMouse, (void*)&detection_data);

                    //std::cout << " current_fps_det = " << current_fps_det << ", current_fps_cap = " << current_fps_cap << std::endl;
                } while (!detection_data.exit_flag);
                // std::cout << " show detection exit \n";  //AgNext, originall was uncomented
                // cv::waitKey(0);     // Agnext (asks for key press before video exit)
                cv::destroyWindow("window");
                writeFile(frame_str, _1lb_count_str, _2lb_count_str, _3lb_count_str, _1Banjhi_count_str, _2Banjhi_count_str, _coarse_count_str, _cluster_count_str, fine_per.substr(0,12), _timer); // Agnext write to file
                // wait for all threads
                if (t_cap.joinable()) t_cap.join();
                if (t_prepare.joinable()) t_prepare.join();
                if (t_detect.joinable()) t_detect.join();
                if (t_post.joinable()) t_post.join();
                if (t_draw.joinable()) t_draw.join();
                if (t_write.joinable()) t_write.join();
                if (t_network.joinable()) t_network.join();

                break;

            }
            else if (file_ext == "txt") {    // list of image files
                std::ifstream file(filename);
                if (!file.is_open()) std::cout << "File not found! \n";
                else
                    for (std::string line; file >> line;) {
                        std::cout << line << std::endl;
                        cv::Mat mat_img = cv::imread(line);
                        std::vector<bbox_t> result_vec = detector.detect(mat_img);
                        // show_console_result(result_vec, obj_names);
                        //draw_boxes(mat_img, result_vec, obj_names);
                        //cv::imwrite("res_" + line, mat_img);
                    }

            }
            else {    // image file
                cv::Mat mat_img = cv::imread(filename);

                auto start = std::chrono::steady_clock::now();
                std::vector<bbox_t> result_vec = detector.detect(mat_img);
                auto end = std::chrono::steady_clock::now();
                std::chrono::duration<double> spent = end - start;
                std::cout << " Time: " << spent.count() << " sec \n";

                //result_vec = detector.tracking_id(result_vec);    // comment it - if track_id is not required
                draw_boxes(mat_img, result_vec, obj_names);
                cv::imshow("window name", mat_img);
                // show_console_result(result_vec, obj_names);
                char key = cvWaitKey(10);   // Agnext
                if(key==27) // Agnext

                    break;  // Agnext
                // cv::waitKey(0);
            }
#else   // OPENCV
            //std::vector<bbox_t> result_vec = detector.detect(filename);

            auto img = detector.load_image(filename);
            std::vector<bbox_t> result_vec = detector.detect(img);
            detector.free_image(img);
            // show_console_result(result_vec, obj_names);

#endif  // OPENCV
        }
        catch (std::exception &e) { std::cerr << "exception: " << e.what() << "\n"; getchar(); }
        catch (...) { std::cerr << "unknown exception \n"; getchar(); }
        filename.clear();
    }

    return 0;
}
