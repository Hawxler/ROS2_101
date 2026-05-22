# Static TF 발행 노드
import rclpy
from rclpy.node import Node

from geometry_msgs.msg import TransformStamped
from tf2_ros.static_transform_broadcaster import StaticTransformBroadcaster

class StaticTfPub1(Node):
    def __init__(self):
        super().__init__('static_tf_pub_node1')
        self.get_logger().info("Static TF Pub 노드 시작")

        #1. StaticTransformBroadcaster 생성
        self.static_broadcaster = StaticTransformBroadcaster(self)

        #2. TransformStamped 메시지 생성
        static_transform = TransformStamped()

        #3. 시간 정보 입력
        static_transform.header.stamp = self.get_clock().now().to_msg()

        #4. 부모 프레임 이름
        static_transform.header.frame_id = 'world'

        #5. 자식 프레임 이름
        static_transform.child_frame_id = 'base_link'

        #6. 변환 정보 입력 (예: x=1.0, y=0.0, z=0.0, 회전은 단위 쿼터니언): world 기준으로 base_link이 x축 방향으로 1.0m 떨어져 있고, 회전은 없음
        static_transform.transform.translation.x = 1.0
        static_transform.transform.translation.y = 0.0
        static_transform.transform.translation.z = 0.0

        #7. 회전 정보 입력 (단위 쿼터니언(회전 없음): x=0.0, y=0.0, z=0.0, w=1.0)
        static_transform.transform.rotation.x = 0.0
        static_transform.transform.rotation.y = 0.0
        static_transform.transform.rotation.z = 0.0
        static_transform.transform.rotation.w = 1.0

        #8. TF 발행
        self.static_broadcaster.sendTransform(static_transform)

        self.get_logger().info("Static TF 발행 완료")

def main(args=None):
    rclpy.init(args=args)

    node1 = StaticTfPub1()
    rclpy.spin(node1)

    node1.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
        main()