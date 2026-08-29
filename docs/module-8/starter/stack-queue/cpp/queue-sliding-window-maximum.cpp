#include <bits/stdc++.h>
using namespace std;

int main() {
    int n, k;
    cin >> n >> k;
    vector<long long> values(n);
    for (auto& value : values) cin >> value;

    // TODO: maintain a deque of candidate maximum indices.
    for (int i = 0; i <= n - k; ++i) cout << (i ? " " : "") << 0;
    cout << '\n';
}
