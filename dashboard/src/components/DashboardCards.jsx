import React, { useEffect, useState } from "react";
import api from "../api/client";

export default function DashboardCards() {

    const [summary, setSummary] = useState(null);

    useEffect(() => {

        api.get("/patients/summary")
            .then((res) => {
                setSummary(res.data);
            });

    }, []);

    if (!summary) {
        return <h3>Loading...</h3>;
    }

    const cards = [
        ["Patients", summary.total_patients],
        ["High Risk", summary.high_risk_patients],
        ["Normal", summary.normal_patients]
    ];

    return (
        <div
            style={{
                display: "grid",
                gridTemplateColumns: "repeat(3,1fr)",
                gap: "20px"
            }}
        >
            {cards.map((card) => (
                <div
                    key={card[0]}
                    style={{
                        border: "1px solid #ddd",
                        borderRadius: "10px",
                        padding: "20px"
                    }}
                >
                    <h3>{card[0]}</h3>
                    <h1>{card[1]}</h1>
                </div>
            ))}
        </div>
    );
}