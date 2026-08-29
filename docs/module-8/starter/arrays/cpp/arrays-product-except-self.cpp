#include <bits/stdc++.h>
using namespace std;

int main() {
    int n;
    cin >> n;
    vector<long long> values(n);
    for (auto& value : values) cin >> value;

    // TODO: build products without using division.
    for (int i = 0; i < n; ++i) cout << (i ? " " : "") << 0;
    cout << '\n';
}
