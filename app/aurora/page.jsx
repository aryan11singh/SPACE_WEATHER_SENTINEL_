import DetailPage from "../../components/DetailPage";

export const metadata = {
  title: "Auroral Oval",
  description: "Current and forecast auroral activity."
};

export default function Page() {
  return (
    <DetailPage
      title="Auroral Oval"
      meta="Current and forecast auroral activity."
      cards={[
        {
          title: "North Hemisphere",
          image: "https://services.swpc.noaa.gov/images/aurora-forecast-northern-hemisphere.jpg",
          alt: "Aurora north"
        },
        {
          title: "South Hemisphere",
          image: "https://services.swpc.noaa.gov/images/aurora-forecast-southern-hemisphere.jpg",
          alt: "Aurora south"
        }
      ]}
    />
  );
}
