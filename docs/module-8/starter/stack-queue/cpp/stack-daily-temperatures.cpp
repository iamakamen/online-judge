#include <bits/stdc++.h>
using namespace std;

int main() {
    int n;
    cin >> n;
    vector<int> temperatures(n);
    for (auto& temperature : temperatures) cin >> temperature;

    // TODO: resolve each next warmer day with a monotonic stack.
    for (int i = 0; i < n; ++i) cout << (i ? " " : "") << 0;
    cout << '\n';
}
