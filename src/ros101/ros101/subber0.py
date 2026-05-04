# Hello World 수신 + 터미널 출력
import rclpy
from rclpy.node import Node
from std_msgs.msg import String

class SubString1(Node):
    def __init__(self):
        super().__init__('sub_node1')
        self.subber = self.create_subscription(
            String,
            'topic_string_1',
            self.listener_callback,
            10
        )
        self.subber

    def listener_callback(self, msg):
        self.get_logger().info('[Subber heard] %s' % msg.data)

def main(args=None):
    rclpy.init(args=args)
    node1 = SubString1()
    rclpy.spin(node1)
    node1.destroy_node()
    rclpy.shutdown()

if __name__=='__main__':
    main()