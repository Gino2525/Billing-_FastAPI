async function apiRequest(url, options = {}) {
    let token = localStorage.getItem("access_token");

    let res = await fetch(url, {
        ...options,
        headers: {
            ...(options.headers || {}),
            "Authorization": "Bearer " + token
        }
    });

    // 🔥 If access token invalid
    if (res.status === 401) {
        const refresh = localStorage.getItem("refresh_token");

        const refreshRes = await fetch("/auth/refresh", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ refresh_token: refresh })
        });

        // ❌ FIX HERE
        if (refreshRes.status === 401) {
            localStorage.clear();
            alert("Session expired or user deleted");
            window.location.href = "/";
            return;
        }

        const data = await refreshRes.json();

        if (!refreshRes.ok) {
            localStorage.clear();
            window.location.href = "/";
            return;
        }

        // 🔥 Save new token
        localStorage.setItem("access_token", data.access_token);

        // 🔁 Retry original request
        return fetch(url, {
            ...options,
            headers: {
                ...(options.headers || {}),
                "Authorization": "Bearer " + data.access_token
            }
        });
    }

    return res;
}