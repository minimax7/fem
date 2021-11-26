#plotly #tkinter #python #graph

시계열 데이터의 시각화 분석을 위하여 파이썬과 plotly, tkinter로 작성한 그래프 뷰어 입니다.


기본 뼈대는 파이썬으로 작성하였습니다.
- 2개의 LOG를 선택하여 X, Y1, Y2를 무작위로 선택할 수 있도록 로직을 구성하였습니다.
- 가독성을 높이려고 if 조건문은 최소화하고자 하였습니다.

GUI는 tkinter로 작성하였습니다.
- 다음의 책을 구매하여 참고하였습니다.
- PacktPublishing/Python-GUI-Programming-Cookbook-Third-Edition

그래프는 plolty로 작성하였습니다.
- 사용자의 원활한 그래프 분석을 위하여 plotly를 선택하였습니다.
- 따라서 그래프를 보기 위해서는 익스플로러를 제외한 웹브라우저가 필요합니다.



1. Time series graph
  - X축이 시간인 Main과 Sub Y축 2개를 갖는 그래프를 그림
  
2. Unit step graph
  - 시계열 데이터 중 X축에 시간이 아닌 이동 거리 혹은 크기 등을 시간 순서대로 애니메이션으로 그림


Using Python 3.9 for body.
- Consider that select X and Two Y axies from Two LOG file.
- To improve readability, Minimize typing if blabla.

Using tkinter for GUI.
- I purchased the book [Python-GUI-Programming-Cookbook] referenced them.
- PacktPublishing/Python-GUI-Programming-Cookbook-Third-Edition

Using plotty for Graphing.
- I have no choice to ploting but plotly. 
- Therefore, to view the graph, a web browser is required except for Internet Explorer.


It is a graph viewer written in Python, plotly, and tkinter for visualization analysis of time series data.

1. Time series graph
   - Draw a graph with two Y axes, Main and Sub, where the X axis is time.
  
2. Unit step graph
   - Animated moving distance or size, etc. include time and etc, on the X-axis of time series data

![time_series](https://user-images.githubusercontent.com/79625703/143581205-4864aff8-23b0-41cf-b8f8-5ed6e0c7c7d8.jpeg)


![unit_plot](https://user-images.githubusercontent.com/79625703/143581180-73f5809f-8cd1-4f90-b78c-84ec22ab26ec.jpeg)
