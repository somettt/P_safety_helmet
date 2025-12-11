from risk_analyzer import analyze_cbr

# ---------------------------
# 테스트용 케이스 입력
# ---------------------------

test_case = {
    "helmet": 0,     # 0 = 미착용, 1 = 착용
    "temp": 33.0,    # 온도(°C)
    "noise": 78.0    # 소음(dB)
}

# ---------------------------
# CBR 분석 실행
# ---------------------------
result = analyze_cbr(test_case)

# ---------------------------
# 결과 출력
# ---------------------------
print("\n========== CBR TEST RESULT ==========")
print(f"입력 케이스: {test_case}")
print(f"CBR 판단결과: {result['cbr_results']}")
print(f"최종 위험도: {result['final_risk']}")
print("======================================\n")
