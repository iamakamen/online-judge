#include <bits/stdc++.h>
using namespace std;

int main() {
    int n, m;
    cin >> n >> m;
    vector<long long> left(n), right(m);
    for (auto& value : left) cin >> value;
    for (auto& value : right) cin >> value;

    // TODO: merge both nondecreasing lists.
    for (int i = 0; i < n; ++i) cout << (i ? " " : "") << left[i];
    cout << '\n';
}
