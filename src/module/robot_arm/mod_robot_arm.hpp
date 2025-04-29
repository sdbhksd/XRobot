#include <comp_cmd.hpp>
#include <vector>

#include "bsp_gpio.h"
#include "bsp_pwm.h"
#include "comp_actuator.hpp"
#include "comp_cmd.hpp"
#include "comp_pid.hpp"
#include "dev_custom_controller.hpp"
#include "dev_mit_motor.hpp"
#include "dev_rm_motor.hpp"
#include "module.hpp"

namespace Module {
class RobotArm {
 public:
  /*机械臂运行模式*/
  typedef enum {
    RELAX, /*放松，电机不输出*/
    WORK_TOP,
    WORK_MID,
    WORK_BOT,
    WORK_CUSTOM_CTRL,
    SAFE,
  } Mode;

  // TODO: pinyin
  typedef enum {
    SET_MODE_RELAX,
    SET_MODE_WORK_TOP,
    SET_MODE_WORK_MID,
    SET_MODE_WORK_BOT,
    SET_MODE_CUSTOM_CTRL,
    SET_MODE_SAFE,
    SET_MODE_XIKUANG,
    SET_MODE_YINKUANG,
    SET_MODE_SAVE1,
    SET_MODE_SAVE2,
    SET_MODE_SKUANG,
    SET_MODE_QKONE,
    SET_MODE_QKTWO,
  } RobotArmEvent;

  typedef struct Param {
    const std::vector<Component::CMD::EventMapItem> EVENT_MAP;
    Component::PosActuator::Param yaw1_actr;
    Component::PosActuator::Param yaw2_actr;
    Component::PosActuator::Param pitch1_actr;
    Component::PosActuator::Param pitch2_actr;
    Component::PosActuator::Param roll1_actr;
    Component::PosActuator::Param roll2_actr;
    Device::MitMotor::Param yaw1_motor;
    Device::MitMotor::Param yaw2_motor;
    Device::MitMotor::Param pitch1_motor;
    Device::MitMotor::Param pitch2_motor;
    Device::MitMotor::Param roll1_motor;
    Device::RMMotor::Param roll2_motor;

    struct {
      float yaw1_max; /*大yaw,180度活动范围*/
      float yaw1_min;
      float pitch1_max; /*pitch1,0,85*/
      float pitch1_min;
      float pitch2_max; /*pitch2，-270,0*/
      float pitch2_min;
      float yaw2_max; /*小yaw,-90,+90*/
      float yaw2_min;
      float roll1_max; /*roll1,0,360*/
      float roll1_min;

    } limit;
    Device::CustomController::Param cust_ctrl;
  } Param;

  RobotArm(Param &param, float control_freq);

  void Control();

  void DamiaoSetAble();
  void DMable();

  void SetMode(Mode mode);

 private:
  Param param_;

  float dt_ = 0.0f;

  uint64_t last_wakeup_ = 0;

  uint64_t now_ = 0;

  Mode mode_ = RELAX;
  Component::PosActuator yaw1_actr_;
  Component::PosActuator yaw2_actr_;
  Component::PosActuator pitch1_actr_;
  Component::PosActuator pitch2_actr_;
  Component::PosActuator roll1_actr_;
  Component::PosActuator roll2_actr_;

  Device::MitMotor yaw1_motor_;
  Device::MitMotor yaw2_motor_;
  Device::MitMotor pitch1_motor_;
  Device::MitMotor pitch2_motor_;
  Device::MitMotor roll1_motor_;
  Device::RMMotor roll2_motor_;

  Device::CustomController custom_ctrl_;
  struct {
    float yaw1_theta_ = 0.019f;
    float pitch1_theta_ = 0;  //-2.634f;
    float pitch2_theta_ = 0;  // 2.924f;
    float roll1_theta_ = 0.0f;
    float yaw2_theta_ = 3.298f;  // 这样的花，他是平的。

    float yaw1_out_ = 0;
    float pitch1_out_ = 0;
    float pitch2_out_ = 0;
    float roll1_out_ = 0;
    float yaw2_out_ = 0;
  } setpoint_;
  struct {
    bool motor_last = 0;
    bool motor_current = 0;
    bool xipan_state_ = 0;
    bool save1 = 0;  // 存矿功能
    bool save2 = 0;
    bool initflag = 1;  // 上电时u就是1,给电机发送一次数据。得到反馈值。
    bool is_first = 1;  // 自定义控制器第一次传角度标志。
  } state_;             // 状态汇总

  System::Thread thread_;
  struct {
    float current[6];
    float prev[6];
    float err[6];
    float angle[6];

  } buffer_;  // 自定义控制器缓冲区

  System::Semaphore ctrl_lock_;

  float setpoint_roll2_ = 0.0f;
  float roll2_speed_ = 0.0f;
  uint32_t last_time_ = 0;
  // uint64_t prev_time_ = 0;  // 用于自定义控制器的计时器

  Component::CMD::GimbalCMD cmd_;
};
}  // namespace Module
