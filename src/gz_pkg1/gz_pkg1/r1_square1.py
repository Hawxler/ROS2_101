# Gazebo robot1을 /odom 기준으로 사각형 주행시키기
import math
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from nav_msgs.msg import Odometry

class SquareDrive(Node):
    def __init__(self):
        super().__init__('r1_square_node1')

        # ===============================
        # 1. 주행 설정값
        # ===============================
        self.target_dist = 2.0   # 한 번 이동 거리(m)
        self.target_angle = math.radians(90.0) #회전각도 rad

        self.linear_speed = 0.5  # 전진속도(m/s)
        self.angular_speed = 0.5 # 회전속도(rad/s)

        self.total_sides = 4     # 4 변
        self.current_side = 0    # 현재 몇 번째 변인지

        # ===============================
        # 2. 현재 위치 / 자세
        # ===============================
        self.current_x = 0.0
        self.current_y = 0.0
        self.current_yaw = 0.0

        # ===============================
        # 3. 각 동작의 시작 기준값
        # ===============================
        self.start_x = None
        self.start_y = None
        self.start_yaw = None

        # ===============================
        # 4. 상태 변수
        # ===============================
        self.state = "WAIT_ODOM"
        # WAIT_ODOM : odom 처음 받을 때까지 대기
        # MOVE      : 전진
        # ROTATE    : 회전
        # STOP      : 완료 후 정지

        # ===============================
        # 5. ROS2 Publisher / Subscriber
        # ===============================
        self.pubber = self.create_publisher(
            Twist,
            '/cmd_vel',
            10
        )

        self.subber = self.create_subscription(
            Odometry,
            '/odom',
            self.odom_callback,
            10
        )

        # ===============================
        # 6. 제어 타이머
        # ===============================
        self.timer_period = 0.1
        self.timer = self.create_timer(
            self.timer_period,
            self.timer_callback
        )

        self.get_logger().info('r1_square1 시작: odom 기반 사각형 주행')

    # ------------------------------
    # (1) quaternion -> yaw 변환
    # ------------------------------
    def quaternion_to_yaw(self, q):
        siny_cosp = 2.0 * (q.w * q.z + q.x * q.y)
        cosy_cosp = 1.0 - 2.0 * (q.y * q.y + q.z * q.z)

        yaw = math.atan2(siny_cosp, cosy_cosp)

        return yaw
    
    # ------------------------------
    # (2) 각도를 -pi ~ +pi 범위로 정리
    # ------------------------------
    def normalize_angle(self, angle):
        while angle > math.pi:
            angle -= 2.0 * math.pi
        
        while angle < -math.pi:
            angle += 2.0 * math.pi
        
        return angle
    
    # ------------------------------
    # (3) /odom 콜백
    # ------------------------------
    def odom_callback(self, msg):
        self.current_x = msg.pose.pose.position.x
        self.current_y = msg.pose.pose.position.y

        q = msg.pose.pose.orientation
        self.current_yaw = self.quaternion_to_yaw(q)

        # 처음 odom을 받으면 시작점 설정
        if self.state == "WAIT_ODOM":
            self.reset_move_start()
            self.state = 'MOVE'

            self.get_logger().info(
                f'odom 수신 시작: x={self.current_x:.2f}, '
                f'y={self.current_y:.2f}, '
                f'yaw={math.degrees(self.current_yaw):.2f}도'
            )

    # ------------------------------
    # (3) 전진 시작 기준점 저장
    # ------------------------------
    def reset_move_start(self):
        self.start_x = self.current_x
        self.start_y = self.current_y

        self.get_logger().info(
            f'MOVE 시작점 저장: x={self.start_x:.2f}, y={self.start_y:.2f}'
        )

    # ------------------------------
    # (4) 회전 시작 기준각 저장
    # ------------------------------
    def reset_rotate_start(self):
        self.start_yaw = self.current_yaw

        self.get_logger().info(
            f'ROTATE 시작각 저장: yaw={math.degrees(self.start_yaw):.2f}도'
        )
    
    # ------------------------------
    # (5) 시작점으로부터 이동거리 계산
    # ------------------------------
    def get_moved_distance(self):
        if self.start_x is None or self.start_y is None:
            return 0.0
        
        dx = self.current_x - self.start_x
        dy = self.current_y - self.start_y

        return math.sqrt(dx * dx + dy * dy)

    # ------------------------------
    # (6) 시작 yaw로부터 회전각 계산
    # ------------------------------
    def get_rotated_angle(self):
        if self.start_yaw is None:
            return 0.0
        
        diff = self.current_yaw - self.start_yaw
        diff = self.normalize_angle(diff)

        return abs(diff)
    
    # ------------------------------
    # (7) /cmd_vel 발행 함수
    # ------------------------------
    def publish_cmd(self, linear_x, angular_z):
        msg = Twist()
        msg.linear.x = linear_x
        msg.angular.z = angular_z

        self.pubber.publish(msg)

    # ------------------------------
    # (8) 제어 타이머 콜백
    # ------------------------------
    def timer_callback(self):
        if self.state == "WAIT_ODOM":
            self.get_logger().info('odom 대기 중...')
            return
        
        if self.state == 'MOVE':
            self.control_move()

        elif self.state == "ROTATE":
            self.control_rotate()

        elif self.state == 'STOP':
            self.publish_cmd(0.0, 0.0)

    # ------------------------------
    # (9) 전진 제어
    # ------------------------------
    def control_move(self):
        moved_dist = self.get_moved_distance()

        if moved_dist < self.target_dist:
            self.publish_cmd(self.linear_speed, 0.0)

            self.get_logger().info(
                f'[MOVE] {self.current_side + 1}번째 변 전진 중: '
                f'{moved_dist:.2f} / {self.target_dist:.2f} m'
            )
        
        else:
            self.publish_cmd(0.0, 0.0)

            self.get_logger().info(
                f'[MOVE 완료] {self.current_side + 1}번째 변 이동 완료: '
                f'{moved_dist:.2f} m'
            )

            # 전진 완료 후 회전 시작
            self.reset_rotate_start()
            self.state = "ROTATE"

    # ------------------------------
    # (10) 회전 제어
    # ------------------------------
    def control_rotate(self):
        rotated_angle = self.get_rotated_angle()

        if rotated_angle < self.target_angle:
            self.publish_cmd(0.0, self.angular_speed)

            self.get_logger().info(
                f'[ROTATE] 회전 중: '
                f'{math.degrees(rotated_angle):.2f} / 90.00 도'
            )
        else:
            self.publish_cmd(0.0, 0.0)

            self.get_logger().info(
                f'[ROTATE 완료] 회전각: {math.degrees(rotated_angle):.2f}도'
            )

            # 한 번 + 한 번 회전 완료
            self.current_side += 1

            # 4변 완료면 정지
            if self.current_side >= self.total_sides:
                self.state = 'STOP'
                self.get_logger().info('사각형 주행 완료: 로봇 장치')
            
            # 아직 남았으면 다음 전진 시작
            else:
                self.reset_move_start()
                self.state = 'MOVE'

    # ------------------------------
    # (11) 종료 전 정지
    # ------------------------------
    def stop_robot(self):
        self.publish_cmd(0.0, 0.0)
        self.get_logger().info('종료 전 로봇 정지 명령 발행')

def main(args=None):
    rclpy.init(args=args)

    node1 = SquareDrive()

    try:
        rclpy.spin(node1)
    except KeyboardInterrupt:
        node1.get_logger().info('Ctrl+C 입력됨')
    finally:
        node1.stop_robot()
        node1.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()