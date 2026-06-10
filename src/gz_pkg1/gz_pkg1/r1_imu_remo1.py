# Arduino MPU6050 값을 Serial로 읽어서,
# Gazebo robot1을 /cmd_vel로 조종함.
import serial
import math
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist

class ImuRemo(Node):
    def __init__(self):
        super().__init__('r1_imu_remo_node1')

        #1. /cmd_vel 발행
        self.pubber = self.create_publisher(
            Twist,
            '/cmd_vel',
            10
        )

        #2. 파라미터 선언(아두이노에서 포트, 보레이트 확인 필요)
        # 기본값 설정(CH340 계열 보드면: /dev/ttyUSB0)
        self.declare_parameter('port', '/dev/ttyACM0')
        self.declare_parameter('baudrate', 115200)
        self.declare_parameter('dead_zone', 10.0)
        self.declare_parameter('max_linear', 0.5)
        self.declare_parameter('max_angular', 0.8)

        # 현재 적용된 값(파라미터가 변경될 경우 등)
        self.port = self.get_parameter('port').value
        self.baudrate = self.get_parameter('baudrate').value
        self.dead_zone = self.get_parameter('dead_zone').value
        self.max_linear = self.get_parameter('max_linear').value
        self.max_angular = self.get_parameter('max_angular').value

        #3. Serial 연결
        try:
            self.ser = serial.Serial(
                self.port,
                self.baudrate,
                timeout=0.05
            )
            self.get_logger().info(
                f'Arduino Serial 연결 성공: {self.port}, {self.baudrate}'
            )
        except Exception as e:
            self.get_logger().error(f'Serial 연결 실패: {e}')
            self.ser = None
        
        # 0.05초마다 serial 읽기 (20Hz)
        self.timer = self.create_timer(0.05, self.timer_callback)

    #4. 속도 제한 기능 준비해둠. 
    def clamp(self, value, min_value, max_value):
        return max(min_value, min(value, max_value))

    #5. imu 신호를 cmd_vel로 변환하는 기능 준비해둠.
    def convert_imu_to_cmd(self, pitch, roll):
        cmd = Twist()

        # dead zone 안쪽이면 0으로 처리
        if abs(pitch) < self.dead_zone:
            linear_x = 0.0

        else:
            # 앞으로 기울이면 pitch가 음수라고 가정함.
            # 실제 방향이 반대면 아래 부호를 바꾸면 됨.
            linear_x = -pitch * 0.03
        
        if abs(roll) < self.dead_zone:
            angular_z = 0.0
        else:
            # 왼쪽/오른쪽 방향이 센서 방향과 반대면 부호 바꿔.
            angular_z = -roll * 0.03
        
        # 전/후진 속도를 최댓값(+max) ~ 최솟값(-max) 사잇값으로 제한: clamp()
        linear_x = self.clamp(linear_x, -self.max_linear, self.max_linear)
        angular_z = self.clamp(angular_z, -self.max_angular, self.max_angular)

        cmd.linear.x = linear_x
        cmd.angular.z = angular_z

        return cmd
    
    def timer_callback(self):
        if self.ser is None:
            return

        try:
            line = self.ser.readline().decode('utf-8').strip()

            if not line:
                return
            
            # 내가 정한 데이터 형식: pitch,roll
            fromIMU = line.split(',')
            if len(fromIMU) != 2:
                self.get_logger().warn(f'Serial 데이터 형식 오류: {line}')
                return
            
            pitch = float(fromIMU[0])
            roll = float(fromIMU[1])

            # imu 리딩값을 /cmd_vel로 변환 및 발행
            cmd = self.convert_imu_to_cmd(pitch, roll)
            self.pubber.publish(cmd)

            self.get_logger().info(
                f'수집한 /cmd_vel 발행: '
                f'pitch={pitch:.2f}, roll={roll:.2f} '
                f'=> linear.x={cmd.linear.x:.2f}, angular.z={cmd.angular.z:.2f}'
            )
        except Exception as e:
            self.get_logger().warn(f'Serial 읽기 오류: {e}')
        
    def stop_robot(self):
        cmd = Twist()
        self.pubber.publish(cmd)
    
    # 부모의 destroy_node()를 Override함. 
    # (시리얼을 닫아주는 기능 추가 위함.)
    def destry_node(self):
        # 내가 정한 기능도 실행하고, 
        self.stop_robot()

        if self.ser is not None:
            self.ser.close()

        # 부모의 기존 destroy_node() 기능도 실행함.    
        super().destroy_node()

def main(args=None):
    rclpy.init(args=args)

    node1 = ImuRemo()

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