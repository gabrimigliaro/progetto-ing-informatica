import DashboardOverviewTotals from "./assets/DashboardOverviewTotals";
import DashboardOverviewPatients from "./assets/DashboardOverviewPatients";

export default function DashboardOverview() {
    return (
        <>
            <DashboardOverviewTotals></DashboardOverviewTotals>
            <DashboardOverviewPatients></DashboardOverviewPatients>
        </>
    );
}