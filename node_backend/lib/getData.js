const {fetchWeatherApi } = require('openmeteo');
require('dotenv').config()

  const getButterflies = async(db)=>{
    const butterfly_collection = db.collection(process.env.BUTTERFLY_COLLECTION_NAME)
    return butterfly_collection.find().toArray()
    

}
const getDays = async(weather_data_collection)=>{
    let days = 0
    let now = new Date()
    //turn into  2025-04-08
    let currentDate = now.toISOString().slice(0,10)
    //cursor is like a Promise. 
    let date_entry_cursor = weather_data_collection.find({"date":currentDate})
    
    //if current date not found we need to query back and see how many days we need
    while(!await date_entry_cursor.hasNext()){
        days+=1
        //setDate sets the day in the Date object, getDate grabs the day
        now.setDate(now.getDate()-1)
        currentDate = now.toISOString().slice(0,10)
        console.log(currentDate)
        date_entry_cursor = weather_data_collection.find({"date":currentDate})
    }
    return days
    


}



//get weather data from api for x amount of days
 const getWeatherData = async(db)=>{
    //check if current day is in database, if not then continue going backwards and get number of days not in db. 
        const weather_data_collection = db.collection(process.env.WEATHER_COLLECTION_NAME)
        const days = await getDays(weather_data_collection)
        let now = new Date()
        let end_date = now.toISOString().slice(0,10)
        now.setDate(now.getDate()-days)
        let start_date = now.toISOString().slice(0,10)
        if(days>0){
            try{
            
            const params = {
                "latitude":  25.7501358009678,
                "longitude": -80.37727024796885,
                "hourly": ["temperature_2m", "relative_humidity_2m"],
                // "past_Days":days,
                "start_date" : start_date,
                "end_date": end_date,
                "forecast_days": 0
            };
            const url = "https://api.open-meteo.com/v1/forecast";
            const responses = await fetchWeatherApi(url, params);
            // Helper function to form time ranges
            const range = (start, stop, step) =>
                Array.from({ length: (stop - start) / step }, (_, i) => start + i * step);

            // Process first location. Add a for-loop for multiple locations or weather models
            const response = responses[0];
            // Attributes for timezone and location
            const utcOffsetSeconds = response.utcOffsetSeconds();
            const timezone = response.timezone();
            const timezoneAbbreviation = response.timezoneAbbreviation();
            const latitude = response.latitude();
            const longitude = response.longitude();

            const hourly = response.hourly();
            // Note: The order of weather variables in the URL query and the indices below need to match!
            const time = range(Number(hourly.time()), Number(hourly.timeEnd()), hourly.interval()).map((t) => new Date((t + utcOffsetSeconds) * 1000))
            const weatherData = {
                hourly: {
                    time: range(Number(hourly.time()), Number(hourly.timeEnd()), hourly.interval()).map(
                        (t) => new Date((t + utcOffsetSeconds) * 1000)
                    ),
                    temperature2m: hourly.variables(0).valuesArray(),
                    relativeHumidity2m: hourly.variables(1).valuesArray(),
                },
            };


            // `weatherData` now contains a simple structure with arrays for datetime and weather data
            let data = []
            let averageTemp = 0
            let averageHumidity = 0
            for (let i = 0; i < weatherData.hourly.time.length; i++) {
            //every 25 entries (data for each day) add up the averages
            averageTemp+=parseInt(weatherData.hourly.temperature2m[i])
            averageHumidity+=parseInt(weatherData.hourly.relativeHumidity2m[i])
            if(i!=0 && i%25==0){
                //calculate the average, theres 25 entries.
                averageTemp = Math.floor(averageTemp/25)
                averageHumidity = Math.floor(averageHumidity/25)
                let averageTempFarenheit =Math.floor((9/5 * averageTemp) + 32)
                data.push({"date":weatherData.hourly.time[i].toISOString().slice(0,10),"temperature":averageTempFarenheit,"humidity":averageHumidity})
                //set back to 0 for next date
                averageTemp = 0
                averageHumidity = 0
            }
            
                
                }
                console.log(data)
                await weather_data_collection.insertMany(data)
                console.log('inserted new weather data')
                //return weather collection after update
                
        
        }

            catch(e){
            return e
            }
            
        }
        //if data up to date. No update required.
        return weather_data_collection.find().toArray()
    }


const mergeButterflyWeatherData =async(db,weather_data,butterfly_data)=>{
  const weatherMap = new Map(weather_data.map(item=>[item.date,item]))
  let mergedArray = []
  mergedArray = butterfly_data.map(butterfly=>{
    const matchedWeatherData = weatherMap.get(butterfly.date)
    return {
      ...butterfly,
      temperature : matchedWeatherData.temperature ? matchedWeatherData.temperature : null,
      humidity : matchedWeatherData.humidity? matchedWeatherData.humidity : null
    }
  })

  const merged_collection = db.collection(process.env.MERGED_COLLECTION_NAME)
  const results = await merged_collection.find().toArray()
  if(results.length>0){
    //delete any existing data. The merged data will be replaced.
    merged_collection.deleteMany()
  }
  merged_collection.insertMany(mergedArray)
  console.log("Updated Merged Collection!")

  
  
}   
   




module.exports.getButterflies = getButterflies
module.exports.getWeatherData = getWeatherData
module.exports.mergeButterflyWeatherData = mergeButterflyWeatherData
