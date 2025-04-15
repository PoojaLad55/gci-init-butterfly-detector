import { getButterflyDataTemperature} from "@/app/lib/butterfly"
import { NextResponse } from "next/server"

// pull butterfly data from DB
export async function GET(req){
    try{
        const butterfly_data = await getButterflyDataTemperature()
        return NextResponse.json({message:"success",data:butterfly_data},{status:200})
    }
    catch(e){
        return NextResponse.json({message:e},{status:500})
    }
}
