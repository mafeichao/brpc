#include "bvar/reducer.h"
#include "bvar/recorder.h"
#include "bvar/window.h"
#include "butil/logging.h"
#include "brpc/server.h"


#include <thread>

DEFINE_int32(int_flag, 8, "...");

uint32_t get_fn(void* arg) { return *((uint32_t*)arg); }

int main() {
    brpc::StartDummyServerAt(8888/*port*/);

    bvar::Adder<uint32_t> adder;
    adder << 1 << 2 << 3;
    LOG(INFO) << "adder:" << adder.get_value();

    bvar::Maxer<uint32_t> maxer;
    maxer << 1 << 2 << 3;
    LOG(INFO) << "maxer:" << maxer.get_value();

    adder << 4 << 5 << 6;
    LOG(INFO) << "adder:" << adder.get_value();

    maxer << 4 << 5 << 6;
    LOG(INFO) << "maxer:" << maxer.get_value();

    bvar::IntRecorder inter;
    inter << 1 << 2 << 3;
    LOG(INFO) << "inter:" << inter.get_value() << "," << inter.average() << "," << inter.average(1.0);

    inter << 4 << 5 << 6;
    LOG(INFO) << "inter:" << inter.get_value() << "," << inter.average() << "," << inter.average(1.0);

    inter << 7 << 8 << 9;
    LOG(INFO) << "inter:" << inter.get_value() << "," << inter.average() << "," << inter.average(1.0);

    inter << -7 << -8 << -9 << -4 << -5 << -6 << -1 << -2 << -3;
    LOG(INFO) << "inter:" << inter.get_value() << "," << inter.average() << "," << inter.average(1.0);

    while(true) {
        bvar::Adder<uint32_t> sum("test_sum");
        bvar::Maxer<uint32_t> max("test_max");
        bvar::IntRecorder intr("test_intr");
        bvar::Window<bvar::Adder<uint32_t>> sum_minute("test_window_sum", &sum, 5);
        bvar::Window<bvar::Maxer<uint32_t>> max_minute("test_window_max", &max, 5);
        bvar::Window<bvar::IntRecorder> int_minute("test_window_intr", &intr, 5);
        bvar::LatencyRecorder latency("test_latency");
        bvar::Status<uint32_t> status("test_status", 0);
        bvar::Status<std::string> str_status("test_str_status", "str0");
        
        std::atomic<uint64_t> step(1);
        bvar::PassiveStatus<uint32_t> passive_status("test_passive_status", get_fn, &step);
        bvar::GFlag gflag("test_gflag", "int_flag");
        while (true) {
          sum << step;
          max << step;
          intr << step;
          latency << step;
          status.set_value(step);
          str_status.set_value("str" + std::to_string(step));
          gflag.set_value(std::to_string(step).c_str());

          ++step;
          std::this_thread::sleep_for(std::chrono::milliseconds(5));
          if (step % 1000 == 0) {
            LOG(INFO) << "sum:" << sum.get_value()
                      << ",sumw:" << sum_minute.get_value()
                      << ",max:" << max.get_value()
                      << ",maxw:" << max_minute.get_value()
                      << ",int:" << intr.get_value()
                      << ",intw:" << int_minute.get_value() << ",step:" << step;
            // break;
          }
        }
    }
    return 0;
}