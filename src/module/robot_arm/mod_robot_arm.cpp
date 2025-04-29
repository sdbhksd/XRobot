#include "mod_robot_arm.hpp"

#include <thread.hpp>

#include "bsp_time.h"
using namespace Module;

RobotArm::RobotArm(Param& param, float control_freq)
    /* 必须按照顺序初始化 */
    : param_(param),
      yaw1_actr_(this->param_.yaw1_actr, control_freq),
      yaw2_actr_(this->param_.yaw2_actr, control_freq),
      pitch1_actr_(this->param_.pitch1_actr, control_freq),
      pitch2_actr_(this->param_.pitch2_actr, control_freq),
      roll1_actr_(this->param_.roll1_actr, control_freq),
      roll2_actr_(this->param_.roll2_actr, control_freq),
      yaw1_motor_(this->param_.yaw1_motor, "RobotArm_Yaw1"),
      yaw2_motor_(this->param_.yaw2_motor, "RobotArm_Yaw2"),
      pitch1_motor_(this->param_.pitch1_motor, "RobotArm_Pitch1"),
      pitch2_motor_(this->param_.pitch2_motor, "RobotArm_Pitch2"),
      roll1_motor_(this->param_.roll1_motor, "RobotArm_Roll1"),
      roll2_motor_(this->param_.roll2_motor, "RobotArm_Roll2"),
      custom_ctrl_(param.cust_ctrl),
      ctrl_lock_(true) {
  memset(&(this->cmd_), 0, sizeof(this->cmd_));

  auto event_callback = [](RobotArmEvent event, RobotArm* robotarm) {
    robotarm->ctrl_lock_.Wait(UINT32_MAX);

    switch (event) {
      case SET_MODE_RELAX:
        robotarm->SetMode(RELAX);
        break;
      case SET_MODE_WORK_TOP:
        robotarm->SetMode(WORK_TOP);
        break;
      case SET_MODE_WORK_MID:
        robotarm->SetMode(WORK_MID);
        break;
      case SET_MODE_WORK_BOT:
        robotarm->SetMode(WORK_BOT);
        break;
      case SET_MODE_XIKUANG:
        // TODO: 编译错误，不存在的枚举
        robotarm->SetMode(XIKUANG);
        break;
      case SET_MODE_SAFE:
        robotarm->SetMode(SAFE);
        break;
      case SET_MODE_CUSTOM_CTRL:
        robotarm->SetMode(WORK_CUSTOM_CTRL);
        break;
      default:
        break;
    }

    robotarm->ctrl_lock_.Post();
  };

  Component::CMD::RegisterEvent<RobotArm*, RobotArmEvent>(
      event_callback, this, this->param_.EVENT_MAP);

  auto robotarm_thread = [](RobotArm* robotarm) {
    auto cmd_sub = Message::Subscriber<Component::CMD::GimbalCMD>("cmd_gimbal");
    // robotarm->DamiaoSetAble();不行
    uint32_t last_online_time = bsp_time_get_ms();
    while (1) {
      cmd_sub.DumpData(robotarm->cmd_);

      robotarm->ctrl_lock_.Wait(UINT32_MAX);
      robotarm->DamiaoSetAble();
      robotarm->Control();

      robotarm->ctrl_lock_.Post();

      robotarm->thread_.SleepUntil(2, last_online_time);
    }
  };

  this->thread_.Create(robotarm_thread, this, "robotarm_thread", 1024,
                       System::Thread::MEDIUM);
}

void RobotArm::
    DamiaoSetAble() {  // 这个函数不是使能函数，而是根据0,1设置电机使能状态//配合relax函数，兼职完美。

  if (this->state_.motor_last == 0 && this->state_.motor_current == 1) {
    this->pitch2_motor_.Enable();
    this->pitch1_motor_.Enable();
    this->roll1_motor_.Enable();
    this->yaw1_motor_.Enable();
    this->yaw2_motor_.Enable();
    this->state_.motor_last = 1;
  }
  if (this->state_.motor_last == 1 && this->state_.motor_current == 0) {
    this->pitch2_motor_.Relax();
    this->pitch1_motor_.Relax();
    this->roll1_motor_.Relax();
    this->yaw1_motor_.Relax();
    this->yaw2_motor_.Relax();
    this->state_.motor_last = 0;
  }
}

void RobotArm::DMable() {
  this->pitch1_motor_.Relax();
  this->pitch2_motor_.Relax();
  this->yaw2_motor_.Relax();
  this->yaw1_motor_.Relax();
  this->roll1_motor_.Relax();
}

void RobotArm::Control() {
  this->now_ = bsp_time_get();
  /* 时间差 */
  this->dt_ = TIME_DIFF(this->last_wakeup_, this->now_);

  this->last_wakeup_ = this->now_;

  float pit_cmd = 0.0f;
  float yaw_cmd = 0.0f;
  yaw_cmd = this->cmd_.eulr.yaw * this->dt_;
  pit_cmd = this->cmd_.eulr.pit * this->dt_;

  switch (this->mode_) {
    case RobotArm::WORK_TOP: {
      this->setpoint_.yaw1_theta_ = Component::Type::CycleValue(
          this->setpoint_.yaw1_theta_ + yaw_cmd * 2.0f);
      this->setpoint_.yaw1_out_ = this->yaw1_actr_.Calculate(
          this->setpoint_.yaw1_theta_, this->yaw1_motor_.raw_speed,
          this->yaw1_motor_.raw_pos_, this->dt_);
      this->yaw1_motor_.SetMit(this->setpoint_.yaw1_out_);

      this->setpoint_.pitch1_theta_ = Component::Type::CycleValue(
          this->setpoint_.pitch1_theta_ + pit_cmd * 2.0f);
      this->setpoint_.pitch1_out_ = this->pitch1_actr_.Calculate(
          this->setpoint_.pitch1_theta_, this->pitch1_motor_.raw_speed,
          this->pitch1_motor_.raw_pos_, this->dt_);
      this->pitch1_motor_.SetMit(this->setpoint_.pitch1_out_);
      break;
    }
    case RobotArm::WORK_MID: {
      this->setpoint_.pitch2_theta_ = Component::Type::CycleValue(
          this->setpoint_.pitch2_theta_ + pit_cmd * 2.0f);
      this->setpoint_.pitch2_out_ = this->pitch2_actr_.Calculate(
          this->setpoint_.pitch2_theta_, this->pitch2_motor_.raw_speed,
          this->pitch2_motor_.raw_pos_, this->dt_);
      this->pitch2_motor_.SetMit(this->setpoint_.pitch2_out_);

      break;
    }
    case RobotArm::WORK_BOT: {
      this->setpoint_.yaw2_theta_ = Component::Type::CycleValue(
          this->setpoint_.yaw2_theta_ + yaw_cmd * 5.0f);
      this->setpoint_.yaw2_out_ = this->yaw2_actr_.Calculate(
          this->setpoint_.yaw2_theta_, this->yaw2_motor_.raw_speed,
          this->yaw2_motor_.raw_pos_, this->dt_);
      this->yaw2_motor_.SetMit(this->setpoint_.yaw2_out_);

      this->setpoint_.roll1_theta_ += pit_cmd * 3.0f;
      clampf(&(this->setpoint_.roll1_theta_), this->param_.limit.roll1_min,
             this->param_.limit.roll1_max);
      this->roll1_motor_.SetPos(this->setpoint_.roll1_theta_);

      this->roll2_speed_ = this->roll2_actr_.Calculate(
          this->setpoint_roll2_, this->roll2_motor_.GetSpeed(),
          this->roll2_motor_.GetAngle(), this->dt_);
      this->roll2_motor_.Control(roll2_speed_);
      break;
    }
    case RobotArm::SAFE: {
      break;
    }

    case RobotArm::RELAX: {
      if (this->state_.initflag) {
        /* 上电先读取角度 */
        this->DMable();
        this->state_.initflag = 0;

        for (int i = 0; i < 500; i++) {
          this->setpoint_.yaw1_theta_ = this->yaw1_motor_.raw_pos_;
          this->setpoint_.pitch1_theta_ = this->pitch1_motor_.raw_pos_;
          this->setpoint_.pitch2_theta_ = this->pitch2_motor_.raw_pos_;
          this->setpoint_.yaw2_theta_ = this->yaw2_motor_.raw_pos_;
          this->setpoint_.roll1_theta_ = this->roll1_motor_.raw_pos_;
        }
      }
      break;
    }
    case RobotArm::WORK_CUSTOM_CTRL: {
      int i = 0;
      for (i = 0; i < 6; i++) {
        if (custom_ctrl_.data_.angle[i] < 0.00000000f) {
          this->buffer_.current[i] = 0.000000f;

        } else if (custom_ctrl_.data_.angle[i] > M_2PI) {
          // TODO: 不能这么搞
          this->buffer_.current[i] = 6.2831;
        } else {
          this->buffer_.current[i] = custom_ctrl_.data_.angle[i];
        }
      }

      this->setpoint_.yaw1_theta_ =
          Component::Type::CycleValue(this->buffer_.current[5] - 2.0f);
      this->setpoint_.yaw1_out_ = this->yaw1_actr_.Calculate(
          this->setpoint_.yaw1_theta_, this->yaw1_motor_.raw_speed,
          this->yaw1_motor_.raw_pos_, this->dt_);
      this->yaw1_motor_.SetMit(this->setpoint_.yaw1_out_);
      break;
    }

    default:
      XB_ASSERT(false);
      return;
  }
}

void RobotArm::SetMode(RobotArm::Mode mode) {
  if (mode == this->mode_) {
    return;
  }
  if (mode != WORK_CUSTOM_CTRL) {
    /* 切换到其他模式，重置is_first */
    this->state_.is_first = 1;
  }
  if (mode == WORK_BOT) {
    this->state_.motor_current = 1;
  }
  if (mode == WORK_MID) {
    this->state_.motor_current = 1;
  }
  if (mode == WORK_TOP) {
    this->state_.motor_current = 1;
  }
  if (mode == SAFE) {
    this->state_.motor_current = 1;
  }
  if (mode == RELAX) {
    this->state_.motor_current = 0;
    this->state_.xipan_state_ = 0;
  }

  this->mode_ = mode;
}
