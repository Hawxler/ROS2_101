#터틀이 원그리기 request 받음 -> 피드백 -> 10초 후 result
import math
import time
import threading

import rclpy
from rclpy.node import Node
from rclpy.action import ActionServer
from rclpy.executors import MultiThreadedExecutor
from rclpy.callback_groups import ReentrantCallbackGroup

from geometry_msgs.msg import Twist
from turtlesim.msg import Pose

from interface_pkg1.action import MyAction2

class CircleActionServer(Node):
    def __init__(self):
        super().__init__('act_circle_srvr_node1')

        # 1. 콜백 그룹 생성
        # execute_callback + pose_callback() 동시 실행
        self.cb_group = ReentrantCallbackGroup()

        # 2. 액션 서버 생성
        self.action_server = ActionServer(
            self,                       # 현재 노드에 서버 생성
            MyAction2,                  # 사용할 액션 타입
            'circle_act1',              # 액션 이름
            self.execute_callback,      # goal 수신 시 실행할 함수
            callback_group=self.cb_group # 콜백 동시 실행 그룹
        )

        # 3. 거북이 이동 위한 발행
        self.cmd_pubber = self.create_publisher(
            Twist,
            '/turtle1/cmd_vel',
            10
        )

        # 4. 거북이의 위치 구독
        self.pose_subber = self.create_subscription(
            Pose,
            '/turtle1/pose',
            self.pose_callback,
            10,
            callback_group=self.cb_group # 콜백 동시 실행 그룹
        )

        self.current_pose = None
        # 멀티스레드에서 동시에 읽거나 덮어쓰지 못하게 하기 위한 lock
        self.pose_lock = threading.Lock() 

    #5. /turtle1/pose 메시지가 들어올 때마다, 
    # 거북 위치(msg) 받아 current_pose 갱신
    def pose_callback(self, msg):
        with self.pose_lock:
            self.current_pose = msg
    
    #6. 현재 포즈 리턴
    def get_pose(self):
        with self.pose_lock:
            return self.current_pose

    #7. 속도 0 = 거북 멈춤    
    def stop_turtle(self):
        msg = Twist()
        msg.linear.x = 0.0
        msg.angular.z = 0.0
        self.cmd_pubber.publish(msg)

    #8. 터틀심 theta 범위: -π ~ π
    # 3.13 -> 3.14 -> -3.13: 약간(총 0.02 라디안) 회전 
    # 하지만, current - previous = -3.13 - 3.13 = -6.26: 거의 1바퀴 회전으로 오산됨.
    # 따라서, 2*3.14 - 3.13 = 0.2 가 됨.
    def normalize_angle_diff(self, current, previous):
        diff = current - previous

        while diff > math.pi:
            diff -= 2.0 * math.pi
        
        while diff < -math.pi:
            diff += 2.0 * math.pi
        
        return diff
    
    #9. goal이 수신되면 실행하는 액션 본체인 콜백 그룹의 함수
    # 수신된 req로 goal_handle 생성
    def execute_callback(self, goal_handle):
        self.get_logger().info('원 그리기 액션 시작')

        #1. 요청값 꺼내기
        target_laps = goal_handle.request.laps
        linear_x = goal_handle.request.linear_x
        angular_z = goal_handle.request.angular_z

        #2. 현재 포즈 가져오기
        pose = self.get_pose()

        if pose is None:
            self.get_logger().error("아직 pose를 못 받음.")
            goal_handle.abort()
            return MyAction2.Result()
        
        #3. 현재 포즈를 시작 상태로 저장
        start_x = pose.x
        start_y = pose.y
        prev_theta = pose.theta   # 이전 각도
        accumulated_angle = 0.0   # 누적 회전 각도

        #4. 피드백 메시지 생성
        feedback_msg = MyAction2.Feedback()

        #5. 속도 명령 메시지
        cmd = Twist()
        cmd.linear.x = linear_x
        cmd.angular.z = angular_z

        #6. 근사 인정 허용치 설정
        # 터틀의 원점과 거리가 0.25 이하면 원점 도달이라고 인정
        tolerance = 0.25

        while rclpy.ok():
            pose = self.get_pose()

            if pose is None:
                time.sleep(0.05)
                continue
            
            # 멈춤
            if goal_handle.is_cancel_requested:
                self.stop_turtle()
                goal_handle.canceled()
                result = MyAction2.Result()
                result.pose_x = pose.x
                result.pose_y = pose.y
                result.pose_theta = pose.theta
                result.result_laps = accumulated_angle / (2.0 * math.pi)
                return result

            # 각도 계산
            diff_theta = self.normalize_angle_diff(pose.theta, prev_theta)
            accumulated_angle += abs(diff_theta)
            prev_theta = pose.theta
            
            # 회전 수 계산
            current_laps = accumulated_angle / (2.0 * math.pi)
            remaining_laps = target_laps - current_laps

            # 잔여 거리 발행
            feedback_msg.remaining_laps = max(remaining_laps, 0.0)
            goal_handle.publish_feedback(feedback_msg)

            # 시작점과의 거리 계산
            dist_from_start = math.sqrt(
                (pose.x - start_x) ** 2 + 
                (pose.y - start_y) ** 2
            )

            self.get_logger().info(
                f'회전 수: {current_laps:.2f}, '
                f'남은 회전: {feedback_msg.remaining_laps:.2f}, '
                f'시작점 거리: {dist_from_start:.2f}'
            )

            # 회전 루프 탈출: 회전 수가 목표 이상 + 원점과의 거리차가 허용치 미만  
            if current_laps >= target_laps and dist_from_start < tolerance:
                break
            
            # 회전 명령 발행
            self.cmd_pubber.publish(cmd)
            time.sleep(0.05)

        # 거북이 멈추고 성공 판정
        self.stop_turtle()
        goal_handle.succeed()

        # 멈춘 자리 좌표
        pose = self.get_pose()

        # 최종 결과(Result) 만들기 
        result = MyAction2.Result()
        result.pose_x = pose.x
        result.pose_y = pose.y
        result.pose_theta = pose.theta
        result.result_laps = accumulated_angle / (2.0 * math.pi)

        self.get_logger().info("원 그리기 액션 성공")
        return result

def main(args=None):
    rclpy.init(args=args)

    node1 = CircleActionServer()

    executor = MultiThreadedExecutor(num_threads=2)
    executor.add_node(node1)

    try:
        executor.spin()
    finally:
        node1.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()