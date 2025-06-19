# ROS Disk Monitor

這是用於 ROS 系統中監控硬碟空間的 Python 程式，支援 dynamic_reconfigure 動態參數調整。

## 檔案說明
- `disk_monitor.py`：主程式，ROS 節點負責硬碟監控與 log 顯示，同時提供 ROS Service 查詢。
- `diskmonitor.cfg`：使用 `dynamic_reconfigure` 設定動態參數（warning/alarm threshold）。

- ## 🚀 功能說明

- 監控所有 **可讀寫的硬碟掛載點**
- 每 30 秒顯示一次目前硬碟使用情況
- 當剩餘空間低於：
  - `warning_threshold_gb`：會用 `rospy.logwarn` 顯示黃色警告
  - `alarm_threshold_gb`：會用 `rospy.logerr` 顯示紅色嚴重警告
- 提供 ROS service：`/disk_status_check`，可查詢目前所有掛載點使用狀況
- 可在運行中使用 `rqt_reconfigure` 動態調整兩個參數（無需重新啟動）

## 使用方式
此程式需運行於已安裝 dynamic_reconfigure 且支援 ROS 的環境中。

- ###  `CMakeLists.txt` 修改範例

  ```cmake
  find_package(catkin REQUIRED COMPONENTS
    rospy
    std_srvs
    dynamic_reconfigure
    ...
  )
  
  generate_dynamic_reconfigure_options(
    cfg/diskmonitor.cfg
  )
  ```

- ##  `package.xml` 加入依賴

```
  <build_depend>dynamic_reconfigure</build_depend>
  <exec_depend>dynamic_reconfigure</exec_depend>
```
- ###  🧪 執行方式

```
  rosrun your_ros_package disk_monitor.py
```

- ###  🛠 Dynamic Reconfigure 使用方式

```
  rosrun rqt_reconfigure rqt_reconfigure  
```

- 選擇 /disk_monitor即可調整：

```
  warning_threshold_gb
  
  alarm_threshold_gb
```

- ### 📡 提供的 ROS Service

```
  rosservice call /disk_status_check
```

- 會回傳目前所有可讀寫硬碟的使用資訊。

