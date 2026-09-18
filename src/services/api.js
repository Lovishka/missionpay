const API_URL = "http://127.0.0.1:8000";

export async function createMission(goal) {
  const token = localStorage.getItem("token");

  console.log("CREATE MISSION TOKEN:", token);

  const response = await fetch(`${API_URL}/api/missions`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    },
    body: JSON.stringify({
      goal: goal.trim(),
    }),
  });

  const data = await response.json();

  if (!response.ok) {
    throw new Error(data.detail || "Failed to create mission");
  }

  return data;
}


export async function evaluateOffer(missionGoal) {
  const token = localStorage.getItem("token");

  console.log("EVALUATE OFFER TOKEN:", token);

  if (!token) {
    throw new Error("Authentication token not found. Please login again.");
  }

  const response = await fetch(
    `${API_URL}/api/missions/evaluate-offer`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify({
        mission_goal: missionGoal,
      }),
    }
  );

  const data = await response.json();

  if (!response.ok) {
    throw new Error(
      data.detail || "Failed to evaluate offer"
    );
  }

  return data;
}
export async function getDataSummary() {
  const token = localStorage.getItem("token");

  if (!token) {
    throw new Error("Authentication token not found.");
  }

  const response = await fetch(
    `${API_URL}/api/data/summary`,
    {
      method: "GET",
      headers: {
        Authorization: `Bearer ${token}`,
      },
    }
  );

  const data = await response.json();

  if (!response.ok) {
    throw new Error(
      data.detail || "Failed to fetch data summary"
    );
  }

  return data;
}
export async function getSalesHistory() {
  const token = localStorage.getItem("token");

  if (!token) {
    throw new Error("Authentication token not found.");
  }

  const response = await fetch(
    `${API_URL}/api/data/sales-history`,
    {
      method: "GET",
      headers: {
        Authorization: `Bearer ${token}`,
      },
    }
  );

  const data = await response.json();

  if (!response.ok) {
    throw new Error(
      data.detail || "Failed to fetch sales history"
    );
  }

  return data;
}
export async function getAgentActivity() {
  const token = localStorage.getItem("token");

  if (!token) {
    throw new Error("Authentication token not found.");
  }

  const response = await fetch(
    `${API_URL}/api/agents/activity`,
    {
      method: "GET",
      headers: {
        Authorization: `Bearer ${token}`,
      },
    }
  );

  const data = await response.json();

  if (!response.ok) {
    throw new Error(
      data.detail || "Failed to fetch agent activity"
    );
  }

  return data;
}
export async function approveMissionAction({
  product_id,
  proposed_price,
  discount_percentage,
  decision,
}) {
  const token = localStorage.getItem("token");

  if (!token) {
    throw new Error("Authentication token not found.");
  }

  const response = await fetch(
    `${API_URL}/api/missions/approval`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify({
        product_id,
        proposed_price,
        discount_percentage,
        decision,
      }),
    }
  );

  const data = await response.json();

  if (!response.ok) {
    throw new Error(
      data.detail || "Approval action failed"
    );
  }

  return data;
}