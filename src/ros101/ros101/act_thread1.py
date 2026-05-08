# Multi-thread 기본 코드 맛보기
# 한 파일에서 멀티로 pub, sub 동시 실행
import rclpy
from rclpy.node import Node
from rclpy.executors import MultiThreadedExecutor

from ros101.pubber1 import TurtlePubber1
from ros101.subber0_1 import TurtleSubber0_1

def main(args=None):
    rclpy.init(args=args)

    subNode = TurtleSubber0_1()
    pubNode = TurtlePubber1()

    executor = MultiThreadedExecutor()

    executor.add_node(subNode)
    executor.add_node(pubNode)

    try:
        executor.spin()
    finally:
        executor.shutdown()
        subNode.destroy_node()
        pubNode.destroy_node()
        rclpy.shutdown()

if __name__=='__main__':
    main()