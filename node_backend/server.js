require('dotenv').config()
const {MongoClient} = require('mongodb')
const { getWeatherData,getButterflies,mergeButterflyWeatherData} = require('./lib/getData')

const mongoUri = process.env.MONGO_URI
const DATABASE_NAME = process.env.DATABASE_NAME
const BUTTERFLY_COLLECTION_NAME = process.env.BUTTERFLY_COLLECTION_NAME
const WEATHER_COLLECTION_NAME = process.env.WEATHER_COLLECTION_NAME
//this way we can set env variables from the docker container. Alter confidence level from container without having to rebuild
const CONFIDENCE_LEVEL = process.env.CONFIDENCE_LEVEL
let client;
let changeStream;
let db;

async function run(){
    
    try{
        client = new MongoClient(mongoUri)
        await client.connect()
        db = client.db(DATABASE_NAME)
        const butterfly_collection = db.collection(BUTTERFLY_COLLECTION_NAME)

        changeStream = butterfly_collection.watch()
        console.log('MongoDB watch stream started')

        //listens to any change
        changeStream.on('change',async (change)=>{
            // make weather api requests for missing days, merge with butterfly data and insert into mergedbutterfly collection
            console.log('Change detected: ',change.operationType)
            //remove entry if below confidence level
            if(change.operationType=='insert'){
                const butterfly_obj = change.fullDocument
                const curr_confidence = butterfly_obj.confidence 
                const butterfly_id = butterfly_obj._id
                if(curr_confidence >= parseFloat(CONFIDENCE_LEVEL)){
                    console.log('Confidence Value accepted')
                    try{
                        //calls api to gete new weather data then returns updated list
                        const weatherData = await getWeatherData(db)
                        //gets list of butterflies, is already updated going into this 
                        const butterflyData = await getButterflies(db)
                        //merge the data and insert into db
                        await mergeButterflyWeatherData(db,weatherData,butterflyData)
                    }
                    catch(e){
                        console.log('MONGO NOT CONNECTING',e)
                    }
                }
                else{
                    console.log('Confidence Value not accepted. Value has been removed.')
                    //remove non-confident butterflies
                    await butterfly_collection.deleteOne({"_id":butterfly_id})
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