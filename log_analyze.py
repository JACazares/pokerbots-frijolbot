import re
import matplotlib.pyplot as plt

def read_gamelog(filename):
    with open(filename) as f:
        raw_data = f.readlines()
    
    scoresA = []
    scoresB = []
    for line in raw_data:
        lineAB = re.match("Round #[0-9]*, A \((-?[0-9]*)\), B \((-?[0-9]*)\)", line)
        lineBA = re.match("Round #[0-9]*, B \((-?[0-9]*)\), A \((-?[0-9]*)\)", line)
        if lineAB:
            scoresA.append(int(lineAB.group(1)))
            scoresB.append(int(lineAB.group(2)))
        elif lineBA:
            scoresA.append(int(lineBA.group(2)))
            scoresB.append(int(lineBA.group(1)))
        else:
            finalLine = re.match("Final, A \((-?[0-9]*)\), B \((-?[0-9]*)\)", line)
            if finalLine:
                scoresA.append(int(finalLine.group(1)))
                scoresB.append(int(finalLine.group(2)))
    
    return (scoresA, scoresB)

if __name__ == "__main__":
    import plotly.graph_objects as go

    scoreA, scoreB = read_gamelog("gamelog.txt")

    delta = [scoreA[i] - scoreA[i - 1] for i in range(1, len(scoreA))]

    fig = go.Figure()

    final_score_text = f"Final, A ({scoreA[-1]}), B ({scoreB[-1]})"
    fig.add_annotation(
        x=len(scoreA),
        y=scoreA[-1],
        text=final_score_text,
        showarrow=True,
        arrowhead=1
    )

    fig.add_trace(go.Scatter(x=list(range(len(scoreA))), y=scoreA, mode='lines+markers', name='Score A', line=dict(color='red')))
    fig.add_trace(go.Scatter(x=list(range(len(delta))), y=delta, mode='lines+markers', name='Delta A', line=dict(color='blue')))
    #fig.add_trace(go.Scatter(x=list(range(1, len(scoreB)+1)), y=scoreB, mode='lines+markers', name='Score B', line=dict(color='green')))

    fig.update_layout(
        title="Player A Scores and Delta",
        xaxis_title="Round",
        yaxis_title="Score",
        legend_title="Legend"
    )

    fig.show()
    pass