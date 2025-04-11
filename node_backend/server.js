require('dotenv').config()
const {MongoClient} = require('mongodb')
const { error } = require('console')
const { getWeatherData,getButterflies,mergeButterflyWeatherData} = require('./lib/getData')

const mongoUri = process.env.MONGO_URI
const DATABASE_NAME = process.env.DATABASE_NAME
const BUTTERFLY_COLLECTION_NAME = process.env.BUTTERFLY_COLLECTION_NAME
const WEATHER_COLLECTION_NAME = process.env.WEATHER_COLLECTION_NAME

let client;
let changeStream;
let db;

async function run(){
    
    try{
        client = new MongoClient(mongoUri)
        await client.connect()
        const db = client.db(DATABASE_NAME)
        const butterfly_collection = db.collection(BUTTERFLY_COLLECTION_NAME)

        changeStream = butterfly_collection.watch()
        console.log('MongoDB watch stream started')

        //listens to any change
        changeStream.on('change',async (change)=>{
            // make weather api requests for missing days, merge with butterfly data and insert into mergedbutterfly collection
            console.log('Change detected: ',change.operationType)
            if(change.operationType=='insert'){
                try{
                    //calls api to gete new weather data then returns updated list
                    const weatherData = await getWeatherData(db)
                    //gets list of butterflies, is already updated going into this 
                    const butterflyData = await getButterflies(db)
                    //merge the data and insert into db
                    await mergeButterflyWeatherData(db,weatherData,butterflyData)
                }
                catch(e){
                    console.log(e)
                }
        }
        
        })
        //error with the stream.
        changeStream.on('error',(error)=>{
            console.error('Change stream error : ',error)
        })

    }   
    catch(e){
        console.error('Error connecting to MongoDB or setting up change stream: ',e)
        //disconnect client if error
        if(client){
            client.close().catch(err=>console.error('Error closing mongdo client',err))
        }
    }
}   

run().catch(console.dir())