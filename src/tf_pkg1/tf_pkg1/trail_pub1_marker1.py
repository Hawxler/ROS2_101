# 프레임이 지나는 자국 표시: tf_b2_2.py에서 발행하는 TF 정보를 이용하여 child1_frame이 지나는 자국을 표시하는 마커 퍼블리셔 노드
import math
import rclpy
from rclpy.node import Node

import tf2_ros
from geometry_msgs.msg import Point
from visualization_msgs.msg import Marker

class TrailMarkerPub1(Node):
    def __init__(self):
        super().__init__('trail_marker_pub_node1')
        self.get_logger().info("Trail Marker Publisher 노드 시작")

        #1. 잔상을 남길 프레임 지정
        self.target_frame = 'child1_frame'
        self.source_frame = 'world'

        #2. 잔상을 저장할 리스트 초기화
        self.trail_markers = []

        #3. TF를 조회하기 위한 버퍼와 listener 생성
        self.tf_buffer = tf2_ros.Buffer()
        self.tf_listener = tf2_ros.TransformListener(self.tf_buffer, self)

        #4. 마커 퍼블리셔 생성
        self.marker_pubber = self.create_publisher(Marker, 'trail_marker_topic1', 10)

        #5. 타이머 설정 (0.1초마다 콜백 함수 호출)
        timer_period = 0.1 # seconds
        self.timer1 = self.create_timer(timer_period, self.timer_callback)

    def timer_callback(self):
        #6. 현 시각 TF 정보 조회(예: 'world'에서 'child1_frame'까지의 변환 정보)
        # TF Buffer 안에서 두 좌표계 간 위치/회전 관계(변환 정보)를 찾아서 TransformStamped 메시지로 반환함.
        try:
            lookup = self.tf_buffer.lookup_transform(
                self.source_frame,    # 기준(부모) 프레임
                self.target_frame,    # 찾을(자식) 프레임
                rclpy.time.Time()    # 최신 TF 정보 조회
            )
        except Exception as e:
            self.get_logger().warn(f"TF 정보 조회 실패: {e}")
            return
    
        #7. 조회한 TF 정보에서 위치 정보 추출
        x = lookup.transform.translation.x
        y = lookup.transform.translation.y
        z = lookup.transform.translation.z
        self.trail_markers.append((x, y, z))

        # 리스트가 100개를 초과하면 가장 오래된 위치 정보 제거
        if len(self.trail_markers) > 100:
            self.trail_markers.pop(0)

        #8. 마커 메시지 생성 및 위치 정보 입력
        marker = Marker()
        marker.header.frame_id = self.source_frame
        marker.header.stamp = self.get_clock().now().to_msg()

        marker.ns = 'frame_trail'
        marker.id = 0
        marker.type = Marker.LINE_STRIP
        marker.action = Marker.ADD

        # LINE_STRIP을 그릴 점들
        marker.points = []
        for mark in self.trail_markers:
            p = Point()
            p.x = mark[0]
            p.y = mark[1]
            p.z = mark[2]
            marker.points.append(p)
        
        # 선 굵기
        marker.scale.x = 0.02 # 2cm

        # 선 색상 (예: 빨간색)
        marker.color.r = 1.0
        marker.color.g = 0.2
        marker.color.b = 0.2
        marker.color.a = 1.0 # 불투명

        #9. 선 수명 (0이면 영구적으로 유지)
        marker.lifetime.sec = 0

        #10. 마커 발행
        self.marker_pubber.publish(marker)

def main(args=None):
    rclpy.init(args=args)

    node1 = TrailMarkerPub1()
    rclpy.spin(node1)

    node1.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()