# Hello World 퍼블리싱 + 터미널 출력
# https://www.notion.so/Pub-Sub-py-1a8a5c22d891808eb95bdc5a400d1913?source=copy_link#1a8a5c22d8918029b110cceb68f093d1
import rclpy
from rclpy.node import Node
from std_msgs.msg import String

class PubString1(Node):
    def __init__(self):
        super().__init__('pub_node1')
        self.pubber = self.create_publisher(
            String,
            'topic_string_1',
            10
        )
        timer_period = 2
        self.timer = self.create_timer(timer_period, self.timer_callback)
        self.count = 0
    
    def timer_callback(self):
        msg = String()
        msg.data = "Hello Hawx! %d" % self.count
        self.pubber.publish(msg)
        self.get_logger().info('[from Pubber] %s' % msg.data)
        self.count += 1

def main(args=None):
    rclpy.init(args=args)
    node1 = PubString1()
    rclpy.spin(node1)
    node1.destroy_node()
    rclpy.shutdown()

if __name__=='__main__':
    main()