import { useEffect, useState } from "react"
import { useDispatch, useSelector } from "react-redux"
import { useHistory } from "react-router-dom"
import { getOrdersThunk } from "../../store/orderPage"
import "./yourOrders.css"

const YourOrders = () => {
    const dispatch = useDispatch()
    const history = useHistory()
    const [isLoaded, setIsLoaded] = useState(false)
    const user = useSelector((state) => state.session.user)

    useEffect(async () => {
        if (!user) {
            history.push('/')
            return
        }
        await dispatch(getOrdersThunk())
        setIsLoaded(true)
    }, [dispatch])

    const orders = useSelector((state) => state.orders)

    return (
        <div className="your-orders-wrapper">
            <h1 className="your-reviews-header">Your Orders</h1>
            {orders?.map((order) => {
                return (
                    <div key={order.id} className="your-orders-order-wrapper">
                        <div className="your-orders-order-border-wrapper">
                            <h2>Ordered {order.totalItems} items on {(new Date(order.orderDate)).toDateString().slice(3,)}</h2>
                            <div className="your-orders-items-wrapper">
                                {order.items?.map((item) => {
                                    return (
                                        <div className="your-orders-item-wrapper" key={item.id}>
                                            <div className="your-orders-item-image" onClick={() => history.push(`/items/${item.id}`)} style={{ backgroundImage: `url(${item.previewImageURL})` }}></div>
                                            <div className="your-orders-item-text-wrapper">
                                                <h4 >Purchased {item.quantity} x <span onClick={() => history.push(`/items/${item.id}`)}>{item.name}</span></h4>
                                                <h5 >Sold by {item.shopName} </h5>
                                                <h6>${item.purchasePrice} x {item.quantity} = ${(item.purchasePrice * item.quantity).toFixed(2)}</h6>
                                            </div>
                                        </div>
                                    )
                                })}
                            </div>
                            <h3>Order total: ${Math.round(order.totalPrice * 100) / 100}</h3>
                        </div>
                    </div>
                )
            })}
        </div>
    )
}

export default YourOrders
