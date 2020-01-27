package main

import "testing"

func Test_parseCode(t *testing.T) {
	type args struct {
		url string
	}
	tests := []struct {
		name string
		args args
		want string
	}{
		{
			name: "big t1",
			args: args{
				url : "http://127.0.0.1:5000/authentication_return?code=AQBzZPftO11imxSz5l-JkUte8_WyIY8HAsoqPyhZzO8XfW-lPcdvBXP6uffHo1GpDGhJ-c72eKjqRvd4lUFp7SlHEDKrB3KXC3aqWAsBN1CYTOZzXX9iGbn7duzbqD_LLxuGZ4CvM7FMi_Zw-u0_FkZpFLSpuQ9SKCvo2Mdui6a5AnHQB1UdoxpcwoCd8lykPwjvlYs6eKLlxqjLUaPDfi7UvmU-mO9fIZLPR5yBJQBRfcBueYZRqHIhzp-nRx7p1pNl1c1A5PyWkKsKAxh2w_XyoDzQLTB6vdrn0exiMW5G8TLipa801Vt-zXjThpxXMdZ3odaWOYvH5sAJRiF-7QgY0W_JrZOxguqUaWQk1yr8inJ1ozoaTw",
			},
			want:"AQBzZPftO11imxSz5l-JkUte8_WyIY8HAsoqPyhZzO8XfW-lPcdvBXP6uffHo1GpDGhJ-c72eKjqRvd4lUFp7SlHEDKrB3KXC3aqWAsBN1CYTOZzXX9iGbn7duzbqD_LLxuGZ4CvM7FMi_Zw-u0_FkZpFLSpuQ9SKCvo2Mdui6a5AnHQB1UdoxpcwoCd8lykPwjvlYs6eKLlxqjLUaPDfi7UvmU-mO9fIZLPR5yBJQBRfcBueYZRqHIhzp-nRx7p1pNl1c1A5PyWkKsKAxh2w_XyoDzQLTB6vdrn0exiMW5G8TLipa801Vt-zXjThpxXMdZ3odaWOYvH5sAJRiF-7QgY0W_JrZOxguqUaWQk1yr8inJ1ozoaTw",
		},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			if got := parseCode(tt.args.url); got != tt.want {
				t.Errorf("parseCode() = %v, want %v", got, tt.want)
			}
		})
	}
}
