#include <bits/stdc++.h>
using namespace std;

int main() {
    int n, k;
    cin >> n >> k;
    vector<long long> values(n);
    for (auto& value : values) cin >> value;

    // TODO: remove the kth node from the end.
    for (int i = 0; i < n; ++i) cout << (i ? " " : "") << values[i];
    cout << '\n';
}
