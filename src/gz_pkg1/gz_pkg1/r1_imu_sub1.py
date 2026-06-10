# Gazebo /imu 토픽을 구독해서 roll, pitch, yaw 출력
import math
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Imu

class ImuSub(Node):
    def __init__(self):
        super().__init__('r1_imu_sub_node1')

        self.subber = self.create_subscription(
            Imu,
            '/imu',
            self.imu_callback,
            10
        )

        self.count = 0
        self.get_logger().info('Gazebo /imu 구독 시작')
    
    def quaternion_to_rpy(self, q):
        x = q.x
        y = q.y
        z = q.z
        w = q.w

        # roll, x축 회전
        sinr_cosp = 2.0 * (w * x + y * z)
        cosr_cosp = 1.0 - 2.0 * (x * x + y * y)
        roll = math.atan2(sinr_cosp, cosr_cosp)

        # pitch, y축 회전
        sinp = 2.0 * (w * y - z * x)

        if abs(sinp) >= 1.0:
            pitch = math.copysign(math.pi / 2.0, sinp)
        else:
            pitch = math.asin(sinp)

        # yaw, z축 회전
        siny_cosp = 2.0 * (w * z + x * y)
        cosy_cosp = 1.0 - 2.0 * (y * y + z * z)
        yaw = math.atan2(siny_cosp, cosy_cosp)

        return roll, pitch, yaw
    
    def imu_callback(self, msg):
        self.count += 1

        # 너무 빠르게 출력되지 않도록 10번에 한 번만 출력
        if self.count % 10 != 0:
            return
        
        roll, pitch, yaw = self.quaternion_to_rpy(msg.orientation)

        roll_deg = math.degrees(roll)
        pitch_deg = math.degrees(pitch)
        yaw_deg = math.degrees(yaw)

        av = msg.angular_velocity
        la = msg.linear_acceleration

        self.get_logger().info(
            f'RPY(deg) '
            f'roll={roll_deg:.2f}, '
            f'pitch={pitch_deg:.2f}, '
            f'yaw={yaw_deg:.2f} | '
            f'gyro z={av.z:.3f}, '
            f'acc x={la.x:.3f}, '
            f'acc y={la.y:.3f}, '
            f'acc z={la.z:.3f}'
        )

def main(args=None):
    rclpy.init(args=args)

    node1 = ImuSub()

    try:
        rclpy.spin(node1)
    except KeyboardInterrupt:
        node1.get_logger().info('Ctrl+C 입력됨')
    finally:
        node1.destroy_node()
        rclpy.shutdown()

if __name__=='__main__':
    main()